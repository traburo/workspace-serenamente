import os




class Config:
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")
    CONTACT_WHATSAPP = os.getenv("CONTACT_WHATSAPP", "56937033936")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
    ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
    INTERNAL_JOB_SECRET = os.getenv("INTERNAL_JOB_SECRET", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-lite-image")
    ENABLE_NO_SHOW_FOLLOWUP = os.getenv("ENABLE_NO_SHOW_FOLLOWUP", "0") == "1"
    STAGING_MODE = os.getenv("STAGING_MODE", "0") == "1"
    STAGING_EMAIL_OVERRIDE = os.getenv("STAGING_EMAIL_OVERRIDE", "")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = APP_ENV in {"staging", "production"}
    MAX_CONTENT_LENGTH = 32 * 1024

