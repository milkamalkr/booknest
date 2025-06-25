import psycopg2
from passlib.context import CryptContext
import uuid

# --- Configuration ---
DB_NAME = "myfastapi"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "localhost"  # or your DB host
DB_PORT = 5432

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = "secret"
hashed_password = pwd_context.hash(password)

# --- User Details ---
user_id = str(uuid.uuid4())
name = "Admin User"
email = "admin@booknest.com"
phone = "9999999999"
is_admin = True
subscription_type = "premium"
max_limit = 1000
current_total = 0

# --- Insert into DB ---
try:
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (id, name, email, phone, is_admin, subscription_type, max_limit, current_total, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id, name, email, phone, is_admin,
        subscription_type, max_limit, current_total, hashed_password
    ))

    conn.commit()
    print("✅ Superuser created successfully!")

except Exception as e:
    print("❌ Error creating superuser:", e)

finally:
    if conn:
        cur.close()
        conn.close()
