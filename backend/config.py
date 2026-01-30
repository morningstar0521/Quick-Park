import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "12dfsghuuitgh34t5y6u7i8o9p0asdfghjkl")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'parking.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = os.environ.get("SESSION_TYPE", "filesystem")  
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "session:"
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"   
    SESSION_COOKIE_SECURE = False      
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 1025))
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@parkingapp.com')

    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'redis')
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/1')
    CACHE_DEFAULT_TIMEOUT = 300 
