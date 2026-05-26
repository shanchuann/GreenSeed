"""Run database/schema.sql against Supabase PostgreSQL directly."""
import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("Installing psycopg2-binary...")
    os.system(f"{sys.executable} -m pip install psycopg2-binary -q")
    import psycopg2

from dotenv import load_dotenv

load_dotenv()

url      = os.environ.get("SUPABASE_URL", "")
password = os.environ.get("DATABASE_PASSWORD", "")

if not url or not password:
    sys.exit("Error: SUPABASE_URL and DATABASE_PASSWORD must be set in .env")

project_ref = url.removeprefix("https://").removesuffix(".supabase.co")

# Prefer the IPv4 session pooler (avoids IPv6 DNS issues on some machines).
# Falls back to direct host if DIRECT=1 env var is set.
if os.environ.get("DIRECT"):
    host, port, user = f"db.{project_ref}.supabase.co", 5432, "postgres"
else:
    # Session-mode pooler: full PostgreSQL feature set including DDL
    region = os.environ.get("SUPABASE_REGION", "ap-east-1")
    host   = f"aws-0-{region}.pooler.supabase.com"
    port   = 5432
    user   = f"postgres.{project_ref}"

print(f"Connecting to {host}:{port} …")

sql = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")

conn = psycopg2.connect(
    host=host, port=port,
    user=user, password=password,
    dbname="postgres", sslmode="require",
)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute(sql)

conn.close()
print("✓ Schema applied successfully.")
