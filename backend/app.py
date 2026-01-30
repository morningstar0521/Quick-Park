import os
import math
from datetime import datetime,timedelta
from pytz import timezone
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from config import Config
from extensions import db, mail, cache
from celery_app import celery, init_celery
from flask_mail import Mail, Message
import random
from models import User, ParkingLot, ParkingSpot, Booking, Revenue, PasswordResetOTP
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies, get_jwt
)
from flask_jwt_extended import decode_token
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from tasks import send_receipt_email_task, notify_new_parking_lot
from jinja2 import Template



def update_parking_spots_for_lot(lot):
    existing_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
    existing_count = len(existing_spots)
    
    if existing_count < lot.total_spots:
        for i in range(existing_count + 1, lot.total_spots + 1):
            new_spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=i,
                is_booked=False,
                spot_revenue=0.0,
                duration_hours=0.0
            )
            
            db.session.add(new_spot)
            
    elif existing_count > lot.total_spots:
        spots_to_delete = ParkingSpot.query.filter(
            ParkingSpot.lot_id == lot.id,
            ParkingSpot.id > lot.total_spots
        ).all()
        for spot in spots_to_delete:
            active_booking = Booking.query.filter_by(spot_id=spot.id, end_time=None).first()
            if not active_booking:
                db.session.delete(spot)
            

    db.session.commit()


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    db.init_app(app)
    cache.init_app(app)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) 
    jwt = JWTManager(app)
    
    app.config['MAIL_SERVER'] = '127.0.0.1' 
    app.config['MAIL_PORT'] = 1025 
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@quickpark.com'
    mail.init_app(app)
    print(f"Mail configuration: {app.config['MAIL_SERVER']} {app.config['MAIL_PORT']}")
    
    init_celery(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
            response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,Accept")
            response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,PATCH,OPTIONS")
            response.headers.add("Access-Control-Max-Age", "3600")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 200

    with app.app_context():
        db.create_all()
        ADMIN_EMAIL = "admin@gmail.com"
        ADMIN_PASSWORD = "Admin@1234"

        admin = User.query.filter_by(email=ADMIN_EMAIL).first()
        if not admin:
            admin = User(full_name="Admin", email=ADMIN_EMAIL, role="admin")
            admin.password_hash = generate_password_hash(ADMIN_PASSWORD) 
            db.session.add(admin)
            db.session.commit()
            print("Admin is Created")
        else:
            print("Admin already exists in DB")
            


    @app.route("/api/register", methods=["POST"])
    def register():
        data = request.get_json()
        full_name = data.get("fullName")
        email = (data.get("email") or "").strip().lower()
        address = data.get("address")
        password = data.get("password")

        if not email or not password:
            return jsonify({"ok": False, "message": "email and password required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"ok": False, "message": "email already registered"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email, 
            full_name=full_name, 
            address=address, 
            password_hash=hashed_password, 
            role="user"
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"ok": True, "message": "User registered successfully"}), 201


    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.get_json()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password")

        user = User.query.filter_by(email=email).first() 
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"ok": False, "message": "Invalid credentials"}), 401
        
        additional_claims = {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "address": user.address,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }

        response_data = {
            "ok": True, 
            "message": "logged in successfully",
            "token": access_token, 
            "user": user_data
        }

        return jsonify(response_data), 200

    @app.route("/api/logout", methods=["POST"])
    @jwt_required(optional=True)
    def logout():
        response = jsonify({"ok": True, "message": "logged out successfully"})
        unset_jwt_cookies(response)
        return response

    @app.route("/api/me", methods=["GET"])
    @jwt_required()
    def me():
        identity = get_jwt_identity()
        claims = get_jwt()
        
        if not identity:
            return jsonify({"ok": False, "message": "Invalid token"}), 401
        
        user_id = int(identity)
        
        user = User.query.get(user_id)
        if user:
            return jsonify({
                "ok": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "full_name": user.full_name,
                    "address": user.address,
                    "avatar_url": user.avatar_url,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
            }), 200
        return jsonify({"ok": False, "user": None}), 404

    @app.route('/api/auth/send-otp', methods=['POST'])
    def send_otp():
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        if not email:
            return jsonify({'ok': False, 'message': 'Email is required'}), 400

        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'ok': False, 
                'message': 'This email does not exist in our database. Please register first.',
                'userExists': False
            }), 404

        try:
            otp = f"{random.randint(0, 999999):06d}"
            expires_at = datetime.now(timezone('Asia/Kolkata')) + timedelta(minutes=15)

            otp_record = PasswordResetOTP.query.filter_by(user_id=user.id).first()
            if otp_record:
                otp_record.otp = otp
                otp_record.expires_at = expires_at
                otp_record.created_at = datetime.now(timezone('Asia/Kolkata'))
            else:
                otp_record = PasswordResetOTP(user_id=user.id, otp=otp, expires_at=expires_at)
                db.session.add(otp_record)
            db.session.commit()

            try:
                msg = Message(
                    subject='Your OTP for Quick Park Password Reset',
                    recipients=[user.email],
                    html=f"<p>Hello {user.full_name or user.email},</p><p>Your password reset OTP is: <b>{otp}</b></p><p>This code will expire in 15 minutes.</p>"
                )
                mail.send(msg)
                print(f"Sent OTP to {user.email}")
            except Exception as e:
                print(f"Error sending OTP email: {e}")

            
            try:
                print(f"OTP for {user.email}: {otp} (expires at {expires_at.isoformat()})")
            except Exception:
                pass

            return jsonify({
                'ok': True, 
                'message': 'OTP has been sent to your email. Please check your inbox.',
                'userExists': True
            }), 200
        except Exception as e:
            print(f"Error generating OTP: {e}")
            return jsonify({'ok': False, 'message': 'Error generating OTP'}), 500

    @app.route('/api/auth/verify-otp', methods=['POST'])
    def verify_otp():
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        otp = (data.get('otp') or '').strip()

        if not email or not otp:
            return jsonify({'ok': False, 'message': 'Email and OTP are required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'ok': False, 'message': 'Invalid OTP or email'}), 400

        otp_record = PasswordResetOTP.query.filter_by(user_id=user.id).first()
        if not otp_record:
            return jsonify({'ok': False, 'message': 'No OTP found. Please request a new one.'}), 400

        now = datetime.now(timezone('Asia/Kolkata'))
        expires = otp_record.expires_at
        try:
            print(f"verify_otp: now={now} tz={now.tzinfo}")
            print(f"verify_otp: otp_record.expires_at (raw)={otp_record.expires_at} type={type(otp_record.expires_at)} tz={getattr(otp_record.expires_at, 'tzinfo', None)}")
        except Exception:
            pass
        try:
            if expires is None:
                raise ValueError('No expires_at on OTP record')
            if expires.tzinfo is None:
               
                expires = timezone('Asia/Kolkata').localize(expires)
            else:
                expires = expires.astimezone(timezone('Asia/Kolkata'))
        except Exception as _:
            try:
                db.session.delete(otp_record)
                db.session.commit()
            except Exception:
                db.session.rollback()
            return jsonify({'ok': False, 'message': 'OTP expired or invalid. Please request a new one.'}), 400

        try:
            print(f"verify_otp: normalized_expires={expires} tz={expires.tzinfo}")
        except Exception:
            pass

        if now > expires:
            try:
                db.session.delete(otp_record)
                db.session.commit()
            except Exception:
                db.session.rollback()
            return jsonify({'ok': False, 'message': 'OTP expired. Please request a new one.'}), 400

        if otp_record.otp != otp:
            return jsonify({'ok': False, 'message': 'Invalid OTP.'}), 400

       
        try:
            reset_token = create_access_token(
                identity=str(user.id),
                additional_claims={'reset_password': True},
                expires_delta=timedelta(minutes=15)
            )
            
            try:
                db.session.delete(otp_record)
                db.session.commit()
            except Exception:
                db.session.rollback()

            return jsonify({'ok': True, 'resetToken': reset_token}), 200
        except Exception as e:
            print(f"Error issuing reset token: {e}")
            return jsonify({'ok': False, 'message': 'Error issuing reset token'}), 500


    @app.route("/api/auth/reset-password", methods=["POST"])
    def reset_password():
        data = request.get_json()
        token = data.get("token")
        new_password = data.get("password")
        
        if not token or not new_password:
            return jsonify({"ok": False, "message": "Token and new password are required"}), 400
            
        try:
            
            decoded_token = decode_token(token)
            user_id = decoded_token.get("sub")  
            reset_claim = decoded_token.get("reset_password", False)
            
            if not user_id or not reset_claim:
                return jsonify({"ok": False, "message": "Invalid reset token"}), 400
                
            user = User.query.get(int(user_id))
            if not user:
                return jsonify({"ok": False, "message": "User not found"}), 404
                
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            
            return jsonify({"ok": True, "message": "Password has been reset successfully"}), 200
            
        except Exception as e:
            print(f"Error resetting password: {e}")
            return jsonify({"ok": False, "message": "Invalid or expired token"}), 400

    @app.route("/api/parking-lots", methods=["GET"])
    @jwt_required()
    def get_parking_lots():
        claims = get_jwt()
        if claims.get("role") not in ["admin", "user"]:
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        lots = ParkingLot.query.all()
        
        return jsonify([{
            "id": lot.id,
            "name": lot.name,
            "address": lot.address,
            "city": lot.city,
            "pincode": lot.pincode,
            "parkingType": lot.parking_type,
            "totalSpots": lot.total_spots,
            "occupiedSpots": lot.occupied_spots,
            "ratePerHour": float(lot.rate_per_hour),
            "revenueGenerated": float(lot.revenue_generated),
            "status": lot.status
        } for lot in lots]),200
    @app.route("/api/admin/parking-lots", methods=["GET"])
    @jwt_required()
    def get_admin_parking_lots():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        lots = ParkingLot.query.all()
        
        return jsonify([{
            "id": lot.id,
            "name": lot.name,
            "address": lot.address,
            "city": lot.city,
            "pincode": lot.pincode,
            "parkingType": lot.parking_type,
            "totalSpots": lot.total_spots,
            "occupiedSpots": lot.occupied_spots,
            "ratePerHour": float(lot.rate_per_hour),
            "revenueGenerated": float(lot.revenue_generated),
            "status": lot.status
        } for lot in lots]),200

    @app.route("/api/parking-lots", methods=["POST"])
    @jwt_required()
    def add_parking_lot():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        data = request.json or {}
        lot = ParkingLot(
            name=data.get("name", ""),
            address=data.get("address", ""),
            city=data.get("city", ""),
            pincode=data.get("pincode", ""),
            parking_type=data.get("parkingType", ""),
            total_spots=data.get("totalSpots", 0),
            occupied_spots=0, 
            rate_per_hour=data.get("ratePerHour", 0.0),
            revenue_generated=0.0, 
            status=data.get("status", "Active"),
        )
        db.session.add(lot)
        db.session.commit()
        update_parking_spots_for_lot(lot)
        
        
        try:
            notify_new_parking_lot(lot.id)
        except Exception as e:
            print(f"Celery error: {e}")
            
        return jsonify({"ok": True, "message": "Parking lot added"}), 201

    @app.route("/api/parking-lots/<int:lot_id>", methods=["PUT"])
    @jwt_required()
    def update_parking_lot(lot_id):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        lot = ParkingLot.query.get_or_404(lot_id)
        data = request.json or {}
        
        new_status = data.get("status", lot.status)
        if new_status in ["Maintenance", "Deactivated"] and new_status != lot.status:
            if lot.occupied_spots > 0:
                return jsonify({
                    "ok": False, 
                    "message": f"Cannot change status to '{new_status}' because there are {lot.occupied_spots} occupied spot(s). Please ensure all spots are vacant before making this change."
                }), 400
        
        lot.name = data.get("name", lot.name)
        lot.address = data.get("address", lot.address)
        lot.city = data.get("city", lot.city)
        lot.pincode = data.get("pincode", lot.pincode)
        lot.parking_type = data.get("parkingType", lot.parking_type)
        lot.total_spots = data.get("totalSpots", lot.total_spots)
        lot.rate_per_hour = data.get("ratePerHour", lot.rate_per_hour)
        lot.status = new_status
        db.session.commit()
        
        update_parking_spots_for_lot(lot)
        return jsonify({"ok": True, "message": "Parking lot updated"})

    @app.route("/api/parking-lots/<int:lot_id>", methods=["DELETE"])
    @jwt_required()
    def delete_parking_lot(lot_id):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        lot = ParkingLot.query.get_or_404(lot_id)
        
        if lot.occupied_spots > 0:
            return jsonify({
                "ok": False, 
                "message": "Cannot delete parking lot with occupied spots. Please ensure all spots are vacant before deletion."
            }), 400
            
        ParkingSpot.query.filter_by(lot_id=lot_id).delete()
        Booking.query.filter_by(lot_id=lot_id).delete()
        
        db.session.delete(lot)
        db.session.commit()
        return jsonify({"ok": True, "message": "Parking lot deleted"})

    @app.route("/api/users/details", methods=["GET"])
    @jwt_required()
    def get_users_with_details():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        users = User.query.filter(User.role != "admin").all()
        data = []
        for user in users:
            total_spent = db.session.query(db.func.sum(Booking.amount_paid)) \
                .filter(Booking.user_id == user.id).scalar() or 0
            bookings = Booking.query.filter_by(user_id=user.id) \
                .order_by(Booking.start_time.desc()).limit(5).all()
            booking_list = [{
                "id": b.id,
                "lot_name": ParkingLot.query.get(b.lot_id).name if b.lot_id else "Unknown Lot",
                "spot_id": b.spot_id,
                "start_time": b.start_time.isoformat() if b.start_time else None,
                "end_time": b.end_time.isoformat() if b.end_time else None,
                "amount_paid": float(b.amount_paid or 0)
            } for b in bookings]
            data.append({
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "total_spent": float(total_spent),
                "created_at": user.created_at.isoformat()
                if hasattr(user, "created_at") and user.created_at else None,
                "bookings": booking_list
            })
        return jsonify(data), 200

    @app.route("/api/users/<int:user_id>", methods=["DELETE"])
    @jwt_required()
    def delete_user(user_id):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        user = User.query.get_or_404(user_id)
        
        try:

            active_bookings = Booking.query.filter_by(user_id=user_id, end_time=None).all()
            for booking in active_bookings:
                
                lot = ParkingLot.query.get(booking.lot_id)
                spot = ParkingSpot.query.filter_by(lot_id=booking.lot_id, id=booking.spot_id).first()
                if lot: lot.occupied_spots = max(0, lot.occupied_spots - 1)
                if spot: spot.is_booked = False
                booking.end_time = datetime.now(timezone('Asia/Kolkata'))
                booking.amount_paid = lot.rate_per_hour if lot else 0.0
            db.session.flush() 

            
            Booking.query.filter_by(user_id=user.id).delete()
            PasswordResetOTP.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()
            return jsonify({"ok": True, "message": f"User {user_id} and their bookings deleted"}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error during user deletion cleanup: {e}")
            return jsonify({"ok": False, "message": "Error deleting user and cleaning up data"}), 500

    @app.route("/api/user/dashboard", methods=["GET"])
    @jwt_required()
    def user_dashboard():
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({"ok": False, "message": "User not found"}), 404
            
        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "address": user.address,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.start_time.desc()).all()
        booking_data = []
        for b in bookings:
            lot = ParkingLot.query.get(b.lot_id)
            spot = ParkingSpot.query.get(b.spot_id)
            booking_data.append({
            "id": b.id,
                "lot_name": lot.name if lot else "Unknown Lot",
                "lot_address": f"{lot.address}, {lot.city}" if lot else "Unknown Address",
            "spot_id": b.spot_id,
                "spot_number": spot.spot_number if spot else b.spot_id,
            "start_time": b.start_time.isoformat() if b.start_time else None,
            "end_time": b.end_time.isoformat() if b.end_time else None,
            "amount_paid": float(b.amount_paid or 0.0),
            "status": "Active" if not b.end_time else "Completed",
            "vehicle_number": b.vehicle_number, 
                "is_active": b.end_time is None,
                "rate_per_hour": float(lot.rate_per_hour) if lot else 0.0,
                "duration_hours": float((b.end_time - b.start_time).total_seconds() / 3600) if b.end_time and b.start_time else 0.0
            })
        return jsonify({"ok": True, "user": user_data, "bookings": booking_data}), 200

    @app.route("/api/bookings/park-out", methods=["POST"])
    @jwt_required()
    def park_out():
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        data = request.json or {}
        booking_id = data.get("bookingId")
        if not booking_id:
            return jsonify({"ok": False, "message": "bookingId is required"}), 400
            
        booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
        
        if not booking:
            return jsonify({"ok": False, "message": "Booking not found or access denied"}), 404
            
        if booking.end_time is not None:
            return jsonify({"ok": False, "message": "Booking is already completed"}), 400
            
        end_time = datetime.now(timezone('Asia/Kolkata'))
        booking.end_time = end_time
        lot = ParkingLot.query.get(booking.lot_id)
        
        start_time = booking.start_time
    
        if start_time.tzinfo is None:
            
            start_time = start_time.replace(tzinfo=timezone('Asia/Kolkata'))
        duration_seconds = (end_time - start_time).total_seconds()
        duration_hours = duration_seconds / 3600
        duration_minutes = duration_seconds / 60
        hours_charged = max(1, math.ceil(duration_hours))
        rate = lot.rate_per_hour if lot else 0.0
        final_amount = hours_charged * rate
        booking.amount_paid = final_amount
        spot = ParkingSpot.query.filter_by(lot_id=booking.lot_id, id=booking.spot_id).first()
        
        if lot:
            lot.occupied_spots = max(0, lot.occupied_spots - 1)
            lot.revenue_generated += final_amount
        
        if spot:
            spot.is_booked = False
            
            spot.spot_revenue = 0.0 
            spot.duration_hours = 0.0 
            
        db.session.commit()
        
        try:
            send_receipt_email_task(booking.id)
        except Exception:
            try:
                send_receipt_email_task(booking.id)
            except Exception as _e:
                app.logger.error(f"Failed to send receipt email: {_e}")
        
        return jsonify({
            "ok": True,
            "message": "Park out successful",
            "booking": {
                "id": booking.id,
                "amount_paid": float(final_amount),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_hours": round(duration_hours, 2),
                "duration_minutes": round(duration_minutes, 2),
                "hours_charged": hours_charged,
                "rate_per_hour": float(rate),
                "lot_name": lot.name if lot else "Unknown",
                "spot_number": spot.spot_number if spot else booking.spot_id,
                "vehicle_number": booking.vehicle_number
            }
        }), 200
        
    @app.route("/api/user/profile", methods=["PUT"])
    @jwt_required()
    def update_user_profile():
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        data = request.json or {}
        full_name = data.get("full_name", "").strip()
        address = data.get("address", "").strip()
        avatar_url = data.get("avatar_url", "").strip()
        
        if not full_name:
            return jsonify({"ok": False, "message": "Full name cannot be empty"}), 400
            
        try:
            user = User.query.get(user_id)
            if user:
                user.full_name = full_name
                user.address = address
                if avatar_url:
                    user.avatar_url = avatar_url
                db.session.commit()
                
                updated_user_data = {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role,
                    "address": user.address,
                    "avatar_url": user.avatar_url,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                return jsonify({
                    "ok": True, 
                    "message": "Profile updated successfully",
                    "user": updated_user_data
                }), 200
            return jsonify({"ok": False, "message": "User not found"}), 404

        except Exception as e:
            db.session.rollback()
            print(f"Error updating profile: {e}")
            return jsonify({"ok": False, "message": "An error occurred during profile update"}), 500
        
    @app.route("/api/admin/metrics", methods=["GET"])
    @jwt_required()
    @cache.cached(timeout=30)
    def get_admin_metrics():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            lots = ParkingLot.query.all()
            total_lots = len(lots)
            total_spots = sum(lot.total_spots for lot in lots)
            occupied_spots = sum(lot.occupied_spots for lot in lots)
            available_spots = total_spots - occupied_spots
            registered_users = User.query.filter(User.role == "user").count()
            active_bookings = Booking.query.filter(Booking.end_time.is_(None)).count()
    
            from datetime import date
            today = date.today()
            revenue_today = db.session.query(db.func.sum(Booking.amount_paid)) \
                .filter(db.func.date(Booking.end_time) == today) \
                .scalar() or 0.0
            
            total_revenue = db.session.query(db.func.sum(Booking.amount_paid)) \
                .filter(Booking.end_time.isnot(None)) \
                .scalar() or 0.0
            
            completed_bookings = Booking.query.filter(Booking.end_time.isnot(None)).count()
            
            metrics = {
                "parkingLots": total_lots,
                "totalSpots": total_spots,
                "availableSpots": available_spots,
                "registeredUsers": registered_users,
                "activeBookings": active_bookings,
                "revenueToday": float(revenue_today),
                "totalRevenue": float(total_revenue),
                "completedBookings": completed_bookings
            }
            
            return jsonify({"ok": True, "metrics": metrics}), 200
            
        except Exception as e:
            print(f"Error fetching metrics: {e}")
            return jsonify({"ok": False, "message": "Error fetching metrics"}), 500

    # BOOKING SYSTEM 
    
    @app.route("/api/user/parking-lots", methods=["GET"])
    @jwt_required()
    def get_user_parking_lots():
        claims = get_jwt()
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            lots = ParkingLot.query.filter(ParkingLot.status == "Active").all()
            lots_data = []
            
            for lot in lots:
                occupied_spots = Booking.query.filter(
                    Booking.lot_id == lot.id,
                    Booking.end_time.is_(None)
                ).count()
                available_spots = lot.total_spots - occupied_spots
                
                lots_data.append({
                    "id": lot.id,
                    "name": lot.name,
                    "address": lot.address,
                    "city": lot.city,
                    "pincode": lot.pincode,
                    "parkingType": lot.parking_type,
                    "totalSpots": lot.total_spots,
                    "availableSpots": available_spots,
                    "ratePerHour": float(lot.rate_per_hour),
                    "status": lot.status
                })
            
            return jsonify({"ok": True, "lots": lots_data}), 200
            
        except Exception as e:
            print(f"Error fetching parking lots: {e}")
            return jsonify({"ok": False, "message": "Error fetching parking lots"}), 500

    @app.route("/api/user/parking-lots/<int:lot_id>/spots", methods=["GET"])
    @jwt_required()
    def get_parking_spots(lot_id):
        claims = get_jwt()
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            lot = ParkingLot.query.get_or_404(lot_id)
            spots = ParkingSpot.query.filter(ParkingSpot.lot_id == lot_id).all()
            
            booked_spot_ids = db.session.query(Booking.spot_id).filter(
                Booking.lot_id == lot_id,
                Booking.end_time.is_(None)
            ).all()
            booked_spot_ids = [spot_id[0] for spot_id in booked_spot_ids]
            
            spots_data = []
            for spot in spots:
                spots_data.append({
                    "id": spot.id,
                    "spot_number": spot.spot_number,
                    "is_available": spot.id not in booked_spot_ids,
                    "lot_id": spot.lot_id
                })
            
            return jsonify({
                "ok": True, 
                "lot": {
                    "id": lot.id,
                    "name": lot.name,
                    "address": lot.address,
                    "city": lot.city,
                    "ratePerHour": float(lot.rate_per_hour)
                },
                "spots": spots_data
            }), 200
            
        except Exception as e:
            print(f"Error fetching user parking spots: {e}")
            return jsonify({"ok": False, "message": "Error fetching parking spots"}), 500

    @app.route("/api/user/bookings", methods=["POST"])
    @jwt_required()
    def create_booking():
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            data = request.json or {}
            lot_id = data.get("lot_id")
            vehicle_number = data.get("vehicle_number", "")
            
            if not lot_id:
                return jsonify({"ok": False, "message": "Lot ID is required"}), 400
            
            existing_booking = Booking.query.filter(
                Booking.user_id == user_id,
                Booking.end_time.is_(None)
            ).first()
            
            if existing_booking:
                return jsonify({"ok": False, "message": "You already have an active booking"}), 400
            
            available_spot = ParkingSpot.query.filter(
                ParkingSpot.lot_id == lot_id,
                ParkingSpot.is_booked == False
            ).first()
            
            if not available_spot:
                return jsonify({"ok": False, "message": "No available spots in this lot"}), 400
            
            spot_is_booked = Booking.query.filter(
                Booking.spot_id == available_spot.id,
                Booking.end_time.is_(None)
            ).first()
            
            if spot_is_booked:
                return jsonify({"ok": False, "message": "No available spots in this lot"}), 400
            
            booking = Booking(
                user_id=user_id,
                lot_id=lot_id,
                spot_id=available_spot.id,
                start_time=datetime.now(timezone('Asia/Kolkata')),
                vehicle_number=vehicle_number
            )
            
            db.session.add(booking)
            
            lot = ParkingLot.query.get(lot_id)
            if lot:
                lot.occupied_spots += 1
            
            available_spot.is_booked = True
            
            db.session.commit()
            
            user = User.query.get(user_id)
            lot = ParkingLot.query.get(lot_id)
            spot = available_spot
            
            try:
               
                template_path = os.path.join(os.path.dirname(__file__), 'templates', 'booking_confirmation.html')
                with open(template_path, 'r') as f:
                    template_content = f.read()
                template = Template(template_content)

                msg = Message(
                    subject=f"Parking Booking Confirmation - {lot.name}",
                    recipients=[user.email],
                    sender="noreply@quickpark.com"
                )
                
                msg.html = template.render(
                    user_name=user.full_name,
                    lot_name=lot.name,
                    spot_number=spot.spot_number,
                    booking_id=booking.id,
                    vehicle_number=vehicle_number,
                    start_time=booking.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    rate_per_hour=lot.rate_per_hour
                )
                
                mail.send(msg)
                print(f"Booking confirmation sent to {user.email}")
            except Exception as e:
                print(f"Error sending booking confirmation: {e}")
            
            return jsonify({
                "ok": True,
                "message": "Booking created successfully",
                "booking": {
                    "id": booking.id,
                    "lot_id": booking.lot_id,
                    "spot_id": booking.spot_id,
                    "spot_number": available_spot.spot_number,
                    "start_time": booking.start_time.isoformat(),
                    "vehicle_number": booking.vehicle_number
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating booking: {e}")
            return jsonify({"ok": False, "message": "Error creating booking"}), 500

    @app.route("/api/user/bookings", methods=["GET"])
    @jwt_required()
    def get_user_bookings():
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            bookings = db.session.query(Booking, ParkingLot, ParkingSpot).join(
                ParkingLot, Booking.lot_id == ParkingLot.id
            ).join(
                ParkingSpot, Booking.spot_id == ParkingSpot.id
            ).filter(
                Booking.user_id == user_id
            ).order_by(Booking.start_time.desc()).all()
            
            bookings_data = []
            for booking, lot, spot in bookings:
                bookings_data.append({
                    "id": booking.id,
                    "lot_name": lot.name,
                    "lot_address": f"{lot.address}, {lot.city}",
                    "spot_id": spot.id,
                    "spot_number": spot.spot_number,
                    "start_time": booking.start_time.isoformat() if booking.start_time else None,
                    "end_time": booking.end_time.isoformat() if booking.end_time else None,
                    "vehicle_number": booking.vehicle_number,
                    "amount_paid": float(booking.amount_paid) if booking.amount_paid else 0.0,
                    "status": "Active" if booking.end_time is None else "Completed",
                    "is_active": booking.end_time is None,
                    "rate_per_hour": float(lot.rate_per_hour),
                    "duration_hours": float((booking.end_time - booking.start_time).total_seconds() / 3600) if booking.end_time and booking.start_time else 0.0
                })
            
            return jsonify({"ok": True, "bookings": bookings_data}), 200
            
        except Exception as e:
            print(f"Error fetching user bookings: {e}")
            return jsonify({"ok": False, "message": "Error fetching bookings"}), 500


    @app.route("/api/user/bookings/<int:booking_id>/receipt", methods=["GET"])
    @jwt_required()
    def get_booking_receipt(booking_id):
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            booking = db.session.query(Booking, ParkingLot).join(
                ParkingLot, Booking.lot_id == ParkingLot.id
            ).filter(
                Booking.id == booking_id,
                Booking.user_id == user_id
            ).first()
            
            if not booking:
                return jsonify({"ok": False, "message": "Booking not found"}), 404
            
            booking_obj, lot = booking
            
            duration_hours = 0
            if booking_obj.end_time:
                start_time = booking_obj.start_time
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone('Asia/Kolkata'))
                end_time = booking_obj.end_time
                if end_time.tzinfo is None:
                    end_time = end_time.replace(tzinfo=timezone('Asia/Kolkata'))
                duration_hours = (end_time - start_time).total_seconds() / 3600
            
            receipt_data = {
                "booking_id": booking_obj.id,
                "customer_name": booking_obj.user.full_name,
                "customer_id": f"UID{booking_obj.user_id}",
                "vehicle_number": booking_obj.vehicle_number,
                "lot_name": lot.name,
                "spot_id": booking_obj.spot_id,
                "start_time": booking_obj.start_time.isoformat(),
                "end_time": booking_obj.end_time.isoformat() if booking_obj.end_time else None,
                "duration_hours": round(duration_hours, 2),
                "rate_per_hour": float(lot.rate_per_hour),
                "amount_paid": float(booking_obj.amount_paid) if booking_obj.amount_paid else 0.0,
                "status": "Completed" if booking_obj.end_time else "Active"
            }
            
            return jsonify({"ok": True, "receipt": receipt_data}), 200
            
        except Exception as e:
            print(f"Error fetching receipt: {e}")
            return jsonify({"ok": False, "message": "Error fetching receipt"}), 500

    @app.route("/api/admin/parking-lots/<int:lot_id>/spots", methods=["GET"])
    @jwt_required()
    def get_admin_parking_spots(lot_id):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            lot = ParkingLot.query.get_or_404(lot_id)
            print(f"Found lot: {lot.name}")
            
            spots = ParkingSpot.query.filter(ParkingSpot.lot_id == lot_id).all()
            print(f"Found {len(spots)} spots for lot {lot_id}")
            
            active_bookings = db.session.query(Booking).options(
                joinedload(Booking.user)
            ).filter(
                Booking.lot_id == lot_id,
                Booking.end_time.is_(None)
            ).all()
            print(f"Found {len(active_bookings)} active bookings")

            active_bookings_map = {b.spot_id: b for b in active_bookings}
            
            spots_data = []
            for spot in spots:
                booking = active_bookings_map.get(spot.id)
                
                spot_data = {
                    "id": spot.id,
                    "spot_number": spot.spot_number,
                    "is_available": not booking,
                    "lot_id": spot.lot_id
                }
                
                if booking:
                    start_time = booking.start_time
                    if start_time.tzinfo is None:
                        start_time = start_time.replace(tzinfo=timezone('Asia/Kolkata'))
                    duration_seconds = (datetime.now(timezone('Asia/Kolkata')) - start_time).total_seconds()
                    duration_hours = duration_seconds / 3600
                    spot_revenue = duration_hours * lot.rate_per_hour
                    
                    spot_data.update({
                        "is_available": False,
                        "booking_id": booking.id,
                        "user_id": booking.user_id,
                        "customer_name": booking.user.full_name, 
                        "vehicle_number": booking.vehicle_number,
                        "start_time": booking.start_time.isoformat(),
                        "duration_hours": round(duration_hours, 2),
                        "spot_revenue": round(spot_revenue, 2)
                    })
                
                spots_data.append(spot_data)
            
            return jsonify({
                "ok": True, 
                "lot": {
                    "id": lot.id,
                    "name": lot.name,
                    "address": lot.address,
                    "city": lot.city,
                    "ratePerHour": float(lot.rate_per_hour)
                },
                "spots": spots_data
            }), 200
            
        except Exception as e:
            print(f"Error fetching admin parking spots: {e}")
            return jsonify({"ok": False, "message": "Error fetching parking spots"}), 500

    @app.route("/api/admin/reports/slots/<int:lot_id>", methods=["GET"])
    @jwt_required()
    def get_slot_reports(lot_id):
        identity = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                return jsonify({"ok": False, "message": "Parking lot not found"}), 404
            
            spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
            slot_reports = []
            
            for spot in spots:
                bookings = Booking.query.filter_by(spot_id=spot.id).all()
                
                total_bookings = len(bookings)
                total_revenue = sum(booking.amount_paid or 0 for booking in bookings)
                
                recent_bookings = bookings[-10:] if bookings else []
                
                slot_report = {
                    "id": spot.id,
                    "spot_number": spot.spot_number,
                    "is_booked": spot.is_booked,
                    "total_bookings": total_bookings,
                    "total_revenue": total_revenue,
                    "recent_bookings": [
                        {
                            "id": booking.id,
                            "start_time": booking.start_time.isoformat(),
                            "end_time": booking.end_time.isoformat() if booking.end_time else None,
                            "duration_hours": ((booking.end_time - booking.start_time).total_seconds() / 3600) if booking.end_time else None,
                            "amount_paid": booking.amount_paid or 0
                        }
                        for booking in recent_bookings
                    ]
                }
                slot_reports.append(slot_report)
            
            return jsonify({
                "ok": True,
                "slot_reports": slot_reports
            }), 200
            
        except Exception as e:
            print(f"Error fetching slot reports: {e}")
            return jsonify({"ok": False, "message": "Error fetching slot reports"}), 500

    @app.route("/api/admin/reports/csv/<int:lot_id>", methods=["GET"])
    @jwt_required()
    def download_slot_reports_csv(lot_id):
        identity = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                return jsonify({"ok": False, "message": "Parking lot not found"}), 404
            
            spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
            
            
            csv_content = "Spot Number,Total Bookings,Total Revenue,Current Status,Average Revenue per Booking,Last Booking Date,Recent Bookings Details\n"
            
            for spot in spots:
                bookings = Booking.query.filter_by(spot_id=spot.id).all()
                total_bookings = len(bookings)
                total_revenue = sum(booking.amount_paid or 0 for booking in bookings)
                avg_revenue = total_revenue / total_bookings if total_bookings > 0 else 0
                status = "Occupied" if spot.is_booked else "Available"
                
                
                last_booking_date = bookings[-1].start_time.strftime('%Y-%m-%d') if bookings else "N/A"
                
               
                recent_bookings = bookings[-10:] if bookings else []
                recent_details = "; ".join([
                    f"ID:{b.id} Date:{b.start_time.strftime('%Y-%m-%d')} Start:{b.start_time.strftime('%H:%M')} End:{b.end_time.strftime('%H:%M') if b.end_time else 'Active'} Duration:{((b.end_time - b.start_time).total_seconds() / 3600) if b.end_time else 0:.1f}h Amount:₹{b.amount_paid or 0}"
                    for b in recent_bookings
                ])
                
                csv_content += f"{spot.spot_number},{total_bookings},{total_revenue:.2f},{status},{avg_revenue:.2f},{last_booking_date},\"{recent_details}\"\n"
            
            
            from flask import Response
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename={lot.name}_slot_reports.csv'
                }
            )
            
        except Exception as e:
            print(f"Error generating CSV: {e}")
            return jsonify({"ok": False, "message": "Error generating CSV"}), 500

    @app.route("/api/admin/reports/slot/<int:slot_id>", methods=["GET"])
    @jwt_required()
    def get_slot_detail(slot_id):
        identity = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            spot = ParkingSpot.query.get(slot_id)
            if not spot:
                return jsonify({"ok": False, "message": "Slot not found"}), 404
            
            
            bookings = Booking.query.filter_by(spot_id=slot_id).all()
            
           
            total_bookings = len(bookings)
            total_revenue = sum(booking.amount_paid or 0 for booking in bookings)
            avg_revenue = total_revenue / total_bookings if total_bookings > 0 else 0
            
            recent_bookings = sorted(bookings, key=lambda x: x.start_time, reverse=True)[:10]
            
            booking_data = []
            for booking in bookings:
                booking_data.append({
                    "id": booking.id,
                    "start_time": booking.start_time.isoformat(),
                    "end_time": booking.end_time.isoformat() if booking.end_time else None,
                    "duration_hours": ((booking.end_time - booking.start_time).total_seconds() / 3600) if booking.end_time else 0,
                    "amount_paid": booking.amount_paid or 0,
                    "user_name": booking.user.full_name,
                    "vehicle_number": booking.vehicle_number
                })
            
            lot = spot.parking_lot
            lot_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
            lot_reports = []
            
            for lot_spot in lot_spots:
                lot_bookings = Booking.query.filter_by(spot_id=lot_spot.id).all()
                lot_total_bookings = len(lot_bookings)
                lot_total_revenue = sum(booking.amount_paid or 0 for booking in lot_bookings)
                
                lot_reports.append({
                    "id": lot_spot.id,
                    "spot_number": lot_spot.spot_number,
                    "total_bookings": lot_total_bookings,
                    "total_revenue": lot_total_revenue
                })
            
            return jsonify({
                "ok": True,
                "slot_data": {
                    "id": spot.id,
                    "spot_number": spot.spot_number,
                    "is_booked": spot.is_booked,
                    "total_bookings": total_bookings,
                    "total_revenue": total_revenue,
                    "avg_revenue": avg_revenue,
                    "recent_bookings": [
                        {
                            "id": booking.id,
                            "start_time": booking.start_time.isoformat(),
                            "end_time": booking.end_time.isoformat() if booking.end_time else None,
                            "duration_hours": ((booking.end_time - booking.start_time).total_seconds() / 3600) if booking.end_time else 0,
                            "amount_paid": booking.amount_paid or 0,
                            "user_name": booking.user.full_name,
                            "vehicle_number": booking.vehicle_number
                        }
                        for booking in recent_bookings
                    ],
                    "all_bookings": booking_data
                },
                "lot_data": {
                    "id": lot.id,
                    "name": lot.name,
                    "address": lot.address
                },
                "lot_reports": lot_reports
            }), 200
            
        except Exception as e:
            print(f"Error fetching slot detail: {e}")
            return jsonify({"ok": False, "message": "Error fetching slot detail"}), 500

    # User Reports Routes
    @app.route("/api/user/reports", methods=["GET"])
    @jwt_required()
    def get_user_reports():
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            bookings = Booking.query.filter_by(user_id=user_id).all()
            
            total_bookings = len(bookings)
            total_spent = sum(booking.amount_paid or 0 for booking in bookings)
            total_hours = sum(
                ((booking.end_time - booking.start_time).total_seconds() / 3600) 
                for booking in bookings if booking.end_time
            )
            
            spot_counts = {}
            for booking in bookings:
                try:
                    spot_key = f"{booking.parking_lot.name} - Spot #{booking.parking_spot.spot_number}"
                    spot_counts[spot_key] = spot_counts.get(spot_key, 0) + 1
                except AttributeError as e:
                    print(f"Error accessing booking relationships: {e}")
                    continue
            
            favorite_spot = max(spot_counts.items(), key=lambda x: x[1])[0] if spot_counts else "N/A"
            
            booking_data = []
            for booking in bookings:
                try:
                    booking_data.append({
                        "id": booking.id,
                        "lot_name": booking.parking_lot.name,
                        "spot_number": booking.parking_spot.spot_number,
                        "start_time": booking.start_time.isoformat(),
                        "end_time": booking.end_time.isoformat() if booking.end_time else None,
                        "total_cost": booking.amount_paid or 0,
                        "duration_hours": ((booking.end_time - booking.start_time).total_seconds() / 3600) if booking.end_time else 0,
                        "status": "Completed" if booking.end_time else "Active"
                    })
                except AttributeError as e:
                    print(f"Error processing booking {booking.id}: {e}")
                    continue
            
            recent_bookings = sorted(bookings, key=lambda x: x.start_time, reverse=True)[:10]
            recent_data = []
            for booking in recent_bookings:
                try:
                    recent_data.append({
                        "id": booking.id,
                        "lot_name": booking.parking_lot.name,
                        "spot_number": booking.parking_spot.spot_number,
                        "start_time": booking.start_time.isoformat(),
                        "end_time": booking.end_time.isoformat() if booking.end_time else None,
                        "total_cost": booking.amount_paid or 0,
                        "duration_hours": ((booking.end_time - booking.start_time).total_seconds() / 3600) if booking.end_time else 0,
                        "status": "Completed" if booking.end_time else "Active"
                    })
                except AttributeError as e:
                    print(f"Error processing recent booking {booking.id}: {e}")
                    continue
            
            return jsonify({
                "ok": True,
                "stats": {
                    "totalBookings": total_bookings,
                    "totalSpent": total_spent,
                    "totalHours": total_hours,
                    "favoriteSpot": favorite_spot
                },
                "bookings": booking_data,
                "recent_bookings": recent_data
            }), 200
            
        except Exception as e:
            print(f"Error fetching user reports: {e}")
            return jsonify({"ok": False, "message": "Error fetching user reports"}), 500

    @app.route("/api/user/reports/csv", methods=["GET"])
    @jwt_required()
    def download_user_csv():
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        
        if claims.get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            bookings = Booking.query.filter_by(user_id=user_id).all()
            
            csv_content = "Booking ID,Date,Location,Spot Number,Start Time,End Time,Duration (Hours),Amount Paid,Status\n"
            
            for booking in bookings:
                duration = ((booking.end_time - booking.start_time).total_seconds() / 3600) if booking.end_time else 0
                status = "Completed" if booking.end_time else "Active"
                
                csv_content += f"{booking.id},{booking.start_time.strftime('%Y-%m-%d')},{booking.parking_lot.name},{booking.parking_spot.spot_number},{booking.start_time.strftime('%H:%M')},{booking.end_time.strftime('%H:%M') if booking.end_time else 'Active'},{duration:.1f},{booking.amount_paid or 0},{status}\n"
            
            from flask import Response
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=user_parking_report_{datetime.now().strftime("%Y%m%d")}.csv'
                }
            )
            
        except Exception as e:
            print(f"Error generating user CSV: {e}")
            return jsonify({"ok": False, "message": "Error generating CSV"}), 500

    @app.route("/api/user/reports/pdf", methods=["GET"])
    @jwt_required()
    def download_user_pdf():
        user_id = get_jwt_identity()
        
        if get_jwt().get("role") != "user":
            return jsonify({"ok": False, "message": "Access denied"}), 403
            
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm
            from reportlab.lib import colors
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from io import BytesIO
            
            user = User.query.get(int(user_id))
            bookings = Booking.query.filter_by(user_id=int(user_id)).all()
            
            if not user:
                return jsonify({"ok": False, "message": "User not found"}), 404
            
            total_bookings = len(bookings)
            total_spent = sum(booking.amount_paid or 0 for booking in bookings)
            total_hours = sum(
                ((booking.end_time - booking.start_time).total_seconds() / 3600) 
                for booking in bookings if booking.end_time
            )
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=12,
                alignment=1,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=20,
                fontName='Helvetica-Bold',
                borderColor=colors.HexColor('#3498db'),
                borderWidth=2,
                borderPadding=8
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                fontName='Helvetica'
            )
            
            story = []
            
            story.append(Paragraph("PARKING MANAGEMENT SYSTEM", title_style))
            story.append(Paragraph("User Parking Report", styles['Heading3']))
            story.append(Spacer(1, 0.4*inch))
            
            user_info_data = [
                [Paragraph("<b>User Name:</b>", normal_style), Paragraph(user.full_name, normal_style)],
                [Paragraph("<b>Email:</b>", normal_style), Paragraph(user.email, normal_style)],
                [Paragraph("<b>Report Generated:</b>", normal_style), Paragraph(datetime.now().strftime('%d-%m-%Y %H:%M:%S'), normal_style)]
            ]
            
            user_info_table = Table(user_info_data, colWidths=[2.5*inch, 3.5*inch])
            user_info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
            ]))
            
            story.append(user_info_table)
            story.append(Spacer(1, 0.4*inch))
            
            story.append(Paragraph("BOOKING SUMMARY", heading_style))
            summary_data = [
                ['Metric', 'Value'],
                ['Total Bookings', str(total_bookings)],
                ['Total Amount Spent', f'Rs. {total_spent:.2f}'],
                ['Total Parking Hours', f'{total_hours:.1f} hours']
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.4*inch))
            
            if bookings:
                story.append(Paragraph("BOOKING HISTORY", heading_style))
                booking_data = [['Date', 'Parking Lot', 'Spot No.', 'Duration', 'Amount', 'Status']]
                
                for booking in bookings:
                    try:
                        duration = ((booking.end_time - booking.start_time).total_seconds() / 3600) if booking.end_time else 0
                        status = "Completed" if booking.end_time else "Active"
                        booking_data.append([
                            booking.start_time.strftime('%d-%m-%Y'),
                            booking.parking_lot.name if booking.parking_lot else 'N/A',
                            f"{booking.parking_spot.spot_number}" if booking.parking_spot else 'N/A',
                            f"{duration:.1f}h",
                            f"Rs. {booking.amount_paid or 0:.2f}",
                            status
                        ])
                    except (AttributeError, TypeError):
                        continue
                
                booking_table = Table(booking_data, colWidths=[1.1*inch, 1.6*inch, 0.9*inch, 0.9*inch, 1.1*inch, 1.0*inch])
                booking_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('TOPPADDING', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 9),
                    ('TOPPADDING', (0, 1), (-1, -1), 9),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
                ]))
                
                story.append(booking_table)
            else:
                story.append(Paragraph("No booking history available.", normal_style))
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("---", styles['Normal']))
            story.append(Paragraph("Report generated by Team Quick Park", styles['Italic']))
            
            doc.build(story)
            buffer.seek(0)
            
            from flask import Response
            return Response(
                buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename=parking_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
                }
            )
            
        except Exception as e:
            print(f"Error generating user PDF: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"ok": False, "message": "Error generating PDF"}), 500

    # ADMIN DASHBOARD CHART ENDPOINTS 
    
    @app.route("/api/admin/occupancy-data", methods=["GET"])
    @jwt_required()
    @cache.cached(timeout=30) 
    def get_occupancy_data():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
        
        try:
            lots = ParkingLot.query.all()
            data = []
            for lot in lots:
                occupancy_rate = 0
                if lot.total_spots > 0:
                    occupancy_rate = round((lot.occupied_spots / lot.total_spots) * 100)
                data.append({
                    "name": lot.name,
                    "occupancy": occupancy_rate,
                    "occupied": lot.occupied_spots,
                    "total": lot.total_spots
                })
            
            return jsonify({"ok": True, "data": data}), 200
        except Exception as e:
            print(f"Error fetching occupancy data: {e}")
            return jsonify({"ok": False, "message": "Error fetching data"}), 500

    @app.route("/api/admin/revenue-data", methods=["GET"])
    @jwt_required()
    @cache.cached(timeout=30)
    def get_revenue_data():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
        
        try:
            from datetime import date
            revenue_data = []
            
            for i in range(6, -1, -1):
                date_obj = datetime.now() - timedelta(days=i)
                date_only = date_obj.date()
                
                daily_revenue = db.session.query(db.func.sum(Booking.amount_paid)) \
                    .filter(
                        db.func.date(Booking.end_time) == date_only,
                        Booking.end_time.isnot(None)
                    ).scalar() or 0.0
                
                revenue_data.append({
                    "date": date_only.strftime("%a"),
                    "revenue": float(daily_revenue)
                })
            
            return jsonify({"ok": True, "data": revenue_data}), 200
        except Exception as e:
            print(f"Error fetching revenue data: {e}")
            return jsonify({"ok": False, "message": "Error fetching data"}), 500

    @app.route("/api/admin/recent-bookings", methods=["GET"])
    @jwt_required()
    @cache.cached(timeout=30)  
    def get_recent_bookings():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
        
        try:
            bookings = Booking.query.order_by(Booking.start_time.desc()).limit(10).all()
            
            data = []
            for booking in bookings:
                user = User.query.get(booking.user_id)
                lot = ParkingLot.query.get(booking.lot_id)
                
                status = "active" if booking.end_time is None else "completed"
                
                duration = 0
                if booking.end_time:
                    duration = (booking.end_time - booking.start_time).total_seconds() / 3600
                
                data.append({
                    "id": f"BK{booking.id:04d}",
                    "user": user.full_name if user else "Unknown",
                    "lot": lot.name if lot else "Unknown",
                    "checkIn": booking.start_time.strftime("%I:%M %p") if booking.start_time else "N/A",
                    "duration": f"{duration:.1f}h" if duration else "Ongoing",
                    "amount": round(booking.amount_paid or 0),
                    "status": status
                })
            
            return jsonify({"ok": True, "data": data}), 200
        except Exception as e:
            print(f"Error fetching recent bookings: {e}")
            return jsonify({"ok": False, "message": "Error fetching bookings"}), 500

    # Parking Lot Analytics Route
    @app.route("/api/admin/reports/lot-analytics/<int:lot_id>", methods=["GET"])
    @jwt_required()
    def get_lot_analytics(lot_id):
        identity = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get("role") != "admin":
            return jsonify({"ok": False, "message": "Access denied"}), 403
        
        try:
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                return jsonify({"ok": False, "message": "Parking lot not found"}), 404
            
            spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
            
            thirty_days_ago = datetime.now(timezone('UTC')) - timedelta(days=30)
            bookings = Booking.query.join(ParkingSpot).filter(
                ParkingSpot.lot_id == lot_id,
                Booking.start_time >= thirty_days_ago
            ).all()
            
            hourly_distribution = {}
            for hour in range(24):
                hourly_distribution[hour] = 0
            
            for booking in bookings:
                hour = booking.start_time.hour
                hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
            
            daily_revenue = {}
            for i in range(30):
                date = (datetime.now() - timedelta(days=i)).date()
                daily_revenue[date.isoformat()] = 0
            
            for booking in bookings:
                date = booking.start_time.date().isoformat()
                if date in daily_revenue:
                    daily_revenue[date] = daily_revenue[date] + (booking.amount_paid or 0)
            
            daily_revenue = dict(sorted(daily_revenue.items()))
            
            occupancy_trend = {}
            for i in range(29, -1, -1):
                date = (datetime.now() - timedelta(days=i)).date()
                date_bookings = [b for b in bookings if b.start_time.date() == date]
                avg_occupied_spots = len(set(b.spot_id for b in date_bookings)) if date_bookings else 0
                occupancy_percent = (avg_occupied_spots / len(spots) * 100) if spots else 0
                occupancy_trend[date.isoformat()] = round(occupancy_percent, 2)
            
            return jsonify({
                "ok": True,
                "analytics": {
                    "hourly_distribution": hourly_distribution,
                    "daily_revenue_trend": daily_revenue,
                    "occupancy_trend": occupancy_trend,
                    "summary": {
                        "total_spots": len(spots),
                        "total_bookings": len(bookings),
                        "total_revenue": sum(b.amount_paid or 0 for b in bookings),
                        "avg_booking_value": sum(b.amount_paid or 0 for b in bookings) / len(bookings) if bookings else 0
                    }
                }
            }), 200
            
        except Exception as e:
            print(f"Error fetching lot analytics: {e}")
            return jsonify({"ok": False, "message": "Error fetching lot analytics"}), 500

    @app.route("/api/admin/reports/lot-csv/<int:lot_id>", methods=["GET"])
    @jwt_required()
    def export_lot_report_csv(lot_id):
        identity = get_jwt_identity()
        claims = get_jwt()
        
        print(f"JWT identity: {identity}, Role: {claims.get('role')}")
        
        if claims.get("role") != "admin":
            print(f"Access denied - user role is {claims.get('role')}, not admin")
            return jsonify({"ok": False, "message": "Access denied"}), 403
        
        try:
            from io import StringIO
            import csv
            
            print(f"Fetching lot {lot_id}")
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                print(f"Lot not found")
                return jsonify({"ok": False, "message": "Parking lot not found"}), 404
            
            print(f"Fetching spots and bookings for lot {lot_id}")

            spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
            
            from datetime import datetime as dt
            today = dt.now().date()
            thirty_days_ago_date = today - timedelta(days=30)
            
            print(f"Looking for bookings after {thirty_days_ago_date}")

            bookings = Booking.query.join(ParkingSpot).filter(
                ParkingSpot.lot_id == lot_id,
                Booking.start_time >= dt.combine(thirty_days_ago_date, dt.min.time())
            ).all()
            print(f"Found {len(spots)} spots and {len(bookings)} bookings")
            
            output = StringIO()
            writer = csv.writer(output)
            
            print("Writing header section")

            writer.writerow(['PARKING LOT REPORT'])
            writer.writerow(['Lot Name', lot.name])
            writer.writerow(['Address', lot.address or 'N/A'])
            writer.writerow(['Report Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['Period', 'Last 30 Days'])
            writer.writerow([])
            
            print("Writing summary statistics")
    
            writer.writerow(['SUMMARY STATISTICS'])
            writer.writerow(['Total Spots', len(spots)])
            writer.writerow(['Total Bookings', len(bookings)])
            total_revenue = sum(b.amount_paid or 0 for b in bookings)
            writer.writerow(['Total Revenue (₹)', f'{total_revenue:.2f}'])
            avg_booking = total_revenue / len(bookings) if bookings else 0
            writer.writerow(['Average Booking Value (₹)', f'{avg_booking:.2f}'])
            
            all_dates = set()
            for b in bookings:
                all_dates.add(b.start_time.date())
            total_spot_days = len(all_dates) * len(spots) if all_dates else 0
            occupied_spot_days = len(set((b.spot_id, b.start_time.date()) for b in bookings))
            avg_occupancy = (occupied_spot_days / total_spot_days * 100) if total_spot_days > 0 else 0
            writer.writerow(['Average Occupancy (%)', f'{avg_occupancy:.2f}'])
            writer.writerow([])
            
            print("Writing spot performance table")
            writer.writerow(['SPOT PERFORMANCE DETAILS'])
            writer.writerow(['Spot #', 'Total Bookings', 'Total Revenue (₹)', 'Avg Revenue (₹)', 'Occupancy (%)', 'Last Booking'])
            
            for spot in sorted(spots, key=lambda s: s.spot_number):
                spot_bookings = [b for b in bookings if b.spot_id == spot.id]
                spot_revenue = sum(b.amount_paid or 0 for b in spot_bookings)
                avg_revenue = spot_revenue / len(spot_bookings) if spot_bookings else 0
                
                spot_dates = set(b.start_time.date() for b in spot_bookings)
                spot_occupancy = (len(spot_dates) / len(all_dates) * 100) if all_dates else 0
                
                last_booking = max(spot_bookings, key=lambda b: b.start_time).start_time if spot_bookings else None
                last_booking_str = last_booking.strftime('%Y-%m-%d %H:%M:%S') if last_booking else 'N/A'
                
                writer.writerow([
                    spot.spot_number,
                    len(spot_bookings),
                    f'{spot_revenue:.2f}',
                    f'{avg_revenue:.2f}',
                    f'{spot_occupancy:.2f}',
                    last_booking_str
                ])
            
            writer.writerow([])
            
            print("Writing daily statistics")
            writer.writerow(['DAILY STATISTICS'])
            writer.writerow(['Date', 'Bookings', 'Revenue (₹)', 'Occupancy (%)', 'Occupied Spots'])
            
            for i in range(29, -1, -1):
                current_date = (datetime.now() - timedelta(days=i)).date()
                date_bookings = [b for b in bookings if b.start_time.date() == current_date]
                date_revenue = sum(b.amount_paid or 0 for b in date_bookings)
                occupied_spots = len(set(b.spot_id for b in date_bookings))
                daily_occupancy = (occupied_spots / len(spots) * 100) if spots else 0
                
                writer.writerow([
                    current_date.isoformat(),
                    len(date_bookings),
                    f'{date_revenue:.2f}',
                    f'{daily_occupancy:.2f}',
                    occupied_spots
                ])
            
            print("Generating CSV response")
            csv_data = output.getvalue()
            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment;filename=parking-lot-{lot_id}-{datetime.now().strftime("%Y-%m-%d")}.csv'
            print("CSV response ready to send")
            return response
            
        except Exception as e:
            print(f"ERROR generating CSV report: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"ok": False, "message": f"Error generating CSV report: {str(e)}"}), 500

    @app.route("/api/admin/reports/test-jwt", methods=["GET"])
    @jwt_required()
    def test_jwt():
        """Test endpoint to verify JWT token and return user role"""
        claims = get_jwt()
        user_id = get_jwt_identity()
        
        return jsonify({
            "ok": True,
            "message": "JWT is valid",
            "user_id": user_id,
            "role": claims.get("role"),
            "email": claims.get("email")
        }), 200

    return app



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)