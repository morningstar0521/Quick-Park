"""
Concurrency test for bookings and park-out.

Fires many parallel requests at the real Flask app (using a throwaway SQLite
database, never your real data) and checks that the database stays consistent.

Run inside the backend container:
    docker compose exec backend python tests/test_concurrency.py
"""
import os
import sys
import tempfile
import threading

# ---- isolate the test: temp DB, no real emails, no Redis needed ----
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["MAIL_SERVER"] = "localhost"
os.environ["MAIL_PORT"] = "1"          # nothing listens here -> email fails fast and is skipped
os.environ["MAIL_USE_TLS"] = "false"
os.environ["CACHE_TYPE"] = "SimpleCache"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_jwt_extended import create_access_token  # noqa: E402
from app import create_app                           # noqa: E402
from extensions import db                            # noqa: E402
from models import User, ParkingLot, ParkingSpot, Booking  # noqa: E402

app = create_app()
PARALLEL = 20


def make_lot(name, spots, rate=50.0):
    lot = ParkingLot(name=name, total_spots=spots, rate_per_hour=rate,
                     occupied_spots=0, revenue_generated=0.0)
    db.session.add(lot)
    db.session.flush()
    for i in range(1, spots + 1):
        db.session.add(ParkingSpot(lot_id=lot.id, spot_number=i, is_booked=False))
    db.session.commit()
    return lot.id


def make_users(prefix, n):
    tokens = []
    for i in range(n):
        u = User(full_name=f"{prefix}{i}", email=f"{prefix}{i}@test.com",
                 password_hash="x", role="user")
        db.session.add(u)
        db.session.flush()
        tokens.append(create_access_token(identity=str(u.id),
                                          additional_claims={"id": u.id, "email": u.email, "role": "user"}))
    db.session.commit()
    return tokens


def fire(requests_):
    """Run all requests at the same instant using a barrier."""
    barrier = threading.Barrier(len(requests_))
    results = [None] * len(requests_)

    def worker(i, method, url, token, body):
        client = app.test_client()
        barrier.wait()
        r = getattr(client, method)(url, json=body, headers={"Authorization": f"Bearer {token}"})
        results[i] = r.status_code

    threads = [threading.Thread(target=worker, args=(i, *req)) for i, req in enumerate(requests_)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


with app.app_context():
    # 1. Many users try to book the SAME spot at the same moment
    print(f"\n[1] {PARALLEL} users book the same spot simultaneously")
    lot1 = make_lot("Race Lot", 1)
    spot1 = ParkingSpot.query.filter_by(lot_id=lot1).first().id
    tokens = make_users("same_spot_", PARALLEL)
    codes = fire([("post", "/api/user/bookings", t,
                   {"lot_id": lot1, "vehicle_number": "MH01AB0001", "spot_id": spot1}) for t in tokens])
    db.session.expire_all()
    check("exactly 1 booking succeeded", codes.count(201) == 1, codes)
    check("exactly 1 active booking on the spot",
          Booking.query.filter_by(spot_id=spot1, end_time=None).count() == 1)
    check("occupied_spots == 1", db.session.get(ParkingLot, lot1).occupied_spots == 1)

    # 2. Auto-assign: more users than spots
    print(f"\n[2] {PARALLEL} users auto-book a lot with 5 spots")
    lot2 = make_lot("Auto Lot", 5)
    tokens = make_users("auto_", PARALLEL)
    codes = fire([("post", "/api/user/bookings", t,
                   {"lot_id": lot2, "vehicle_number": "MH01AB0002"}) for t in tokens])
    db.session.expire_all()
    active = Booking.query.filter_by(lot_id=lot2, end_time=None).all()
    check("exactly 5 bookings succeeded", codes.count(201) == 5, codes)
    check("5 different spots used", len({b.spot_id for b in active}) == 5)
    check("occupied_spots == 5", db.session.get(ParkingLot, lot2).occupied_spots == 5)
    check("all 5 spots marked booked",
          ParkingSpot.query.filter_by(lot_id=lot2, is_booked=True).count() == 5)

    # 3. Same user double-clicks "Book" many times
    print(f"\n[3] One user sends {PARALLEL} booking requests at once")
    lot3 = make_lot("Double Click Lot", 10)
    token = make_users("clicker_", 1)[0]
    codes = fire([("post", "/api/user/bookings", token,
                   {"lot_id": lot3, "vehicle_number": "MH01AB0003"}) for _ in range(PARALLEL)])
    db.session.expire_all()
    check("exactly 1 booking succeeded", codes.count(201) == 1, codes)
    check("occupied_spots == 1", db.session.get(ParkingLot, lot3).occupied_spots == 1)

    # 4. Same booking parked-out many times at once (billing must happen once)
    print(f"\n[4] {PARALLEL} park-out requests for the same booking")
    booking = Booking.query.filter_by(lot_id=lot3, end_time=None).first()
    codes = fire([("post", "/api/bookings/park-out", token, {"bookingId": booking.id})
                  for _ in range(PARALLEL)])
    db.session.expire_all()
    lot = db.session.get(ParkingLot, lot3)
    check("exactly 1 park-out succeeded", codes.count(200) == 1, codes)
    check("revenue charged once (50.0)", lot.revenue_generated == 50.0, lot.revenue_generated)
    check("occupied_spots back to 0", lot.occupied_spots == 0)
    check("spot released", ParkingSpot.query.filter_by(lot_id=lot3, is_booked=True).count() == 0)

    # 5. Normal flow still works: book -> park out -> book again
    print("\n[5] Normal single-user flow")
    lot5 = make_lot("Normal Lot", 2)
    token = make_users("normal_", 1)[0]
    c = app.test_client()
    h = {"Authorization": f"Bearer {token}"}
    r1 = c.post("/api/user/bookings", json={"lot_id": lot5, "vehicle_number": "MH01AB0005"}, headers=h)
    bid = r1.get_json().get("booking", {}).get("id")
    r2 = c.post("/api/bookings/park-out", json={"bookingId": bid}, headers=h)
    r3 = c.post("/api/user/bookings", json={"lot_id": lot5, "vehicle_number": "MH01AB0005"}, headers=h)
    check("book -> 201", r1.status_code == 201, r1.get_json())
    check("park out -> 200", r2.status_code == 200, r2.get_json())
    check("book again -> 201", r3.status_code == 201, r3.get_json())

print(f"\nResult: {passed} passed, {failed} failed")
os.unlink(_tmp.name)
sys.exit(1 if failed else 0)
