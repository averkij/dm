import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS


DB_PATH = os.path.join(os.path.dirname(__file__), 'dm.db')


def ensure_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER NOT NULL,
                time INTEGER NOT NULL,
                mode INTEGER NOT NULL,
                user TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        try:
            conn.execute("ALTER TABLE times ADD COLUMN user TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        conn.commit()


def insert_time(number_value: int, time_ms: int, mode_value: int, user_value: str | None) -> int:

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO times (number, time, mode, user, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (number_value, time_ms, mode_value, user_value, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid


app = Flask(__name__)
CORS(app)


@app.route('/api/write_time', methods=['POST'])
def write_time():

    if not request.is_json:
        return jsonify({"error": "Expected application/json body"}), 400

    data = request.get_json(silent=True) or {}
    try:
        number_raw = data.get('number')
        time_raw = data.get('time')
        mode_raw = data.get('mode')
        user_raw = data.get('user')

        if number_raw is None or time_raw is None or mode_raw is None:
            raise ValueError('Missing required fields: number, time, mode')

        number_value = int(str(number_raw))
        time_ms = int(str(time_raw))
        mode_value = int(str(mode_raw))

        if mode_value not in (1, 2):
            raise ValueError('mode must be 1 or 2')

        user_value = None if user_raw in (None, "") else str(user_raw)[:255]

        print(user_value)
        print(mode_value)
        print(number_value)
        print(time_ms)
        print("*"*80)

        row_id = insert_time(number_value, time_ms, mode_value, user_value)
        return jsonify({"status": "ok", "id": row_id})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


@app.route('/api/get_time', methods=['GET'])
def get_time():
    """Return all time rows filtered by user and mode.

    Query params:
    - user: string (optional, if omitted returns rows with NULL user)
    - mode: 1 or 2 (required)
    """
    mode_param = request.args.get('mode', type=int)
    user_param = request.args.get('user', default=None, type=str)
    if mode_param not in (1, 2):
        return jsonify({"error": "mode must be 1 or 2"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        if user_param is None or user_param == "":
            cursor = conn.execute(
                "SELECT id, number, time, mode, user, created_at FROM times WHERE mode = ? ORDER BY id DESC",
                (mode_param,),
            )
        else:
            cursor = conn.execute(
                "SELECT id, number, time, mode, user, created_at FROM times WHERE mode = ? AND user = ? ORDER BY id DESC",
                (mode_param, user_param),
            )
        rows = [dict(r) for r in cursor.fetchall()]
        print(rows)
    return jsonify({"rows": rows})


def main() -> None:

    ensure_db()
    port = int(os.environ.get('PORT', '8000'))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()


