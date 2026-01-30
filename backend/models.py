from datetime import datetime
from pytz import timezone
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model): 
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user")  
    address = db.Column(db.String(256), nullable=True)
    avatar_url = db.Column(db.Text, nullable=True) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone('Asia/Kolkata')))
    bookings = db.relationship("Booking", backref="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        
        return str(self.id)

class ParkingLot(db.Model):
    __tablename__ = "parking_lots"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    pincode = db.Column(db.String(20))
    parking_type = db.Column(db.String(50))  
    total_spots = db.Column(db.Integer, nullable=False)
    occupied_spots = db.Column(db.Integer, default=0)
    rate_per_hour = db.Column(db.Float, nullable=False)
    revenue_generated = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="Active")

    spots = db.relationship("ParkingSpot", backref="lot", cascade="all, delete")

class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"))
    spot_number = db.Column(db.Integer, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    duration_hours = db.Column(db.Integer, default=0)
    spot_revenue = db.Column(db.Float, default=0.0)

class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"))
    spot_id = db.Column(db.Integer, db.ForeignKey("parking_spots.id"))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    amount_paid = db.Column(db.Float, default=0.0)
    vehicle_number = db.Column(db.String(20), default="")
    
    parking_lot = db.relationship("ParkingLot", backref="bookings")
    parking_spot = db.relationship("ParkingSpot", backref="bookings")

class Revenue(db.Model):
    __tablename__ = "revenue"
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"))
    date = db.Column(db.Date)
    total_revenue = db.Column(db.Float, default=0.0)

class PasswordResetOTP(db.Model):
    __tablename__ = 'password_reset_otps'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    otp = db.Column(db.String(10), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone('Asia/Kolkata')))

    user = db.relationship('User', backref='password_reset_otps')