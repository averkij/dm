from main import app, ensure_db

# Ensure the SQLite DB and schema exist before serving
ensure_db()
