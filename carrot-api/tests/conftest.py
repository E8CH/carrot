import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_db")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test_service_key")
os.environ.setdefault("JWT_SECRET", "test_jwt_secret_for_unit_tests")
