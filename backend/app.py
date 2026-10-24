
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
from datetime import datetime, timezone, timedelta
import sqlite3
import os
import joblib

app = Flask(__name__)
CORS(app)

# ---------------- FILE PATHS ----------------

DATABASE = Path(__file__).resolve().parent / "events.db"
MODEL_PATH = Path(__file__).resolve().parent / "model.joblib"

# ---------------- API SECURITY ----------------

API_KEY = os.environ.get("RAKSHA_API_KEY")

# ---------------- ALLOWED VALUES ----------------

VALID_RISK_LEVELS = {"Benign", "Suspicious", "Malicious"}

VALID_STATUSES = {
    "New",
    "Reviewed",
    "False Positive",
    "Escalated",
}

# ---------------- LOAD TRAINED ML MODEL ----------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found at {MODEL_PATH}. "
        "Please run: python ml/train_model.py"
    )

model = joblib.load(MODEL_PATH)


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_log TEXT NOT NULL,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                confidence REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'New'
            )
        """)

        # Migrate old status values without deleting events.
        conn.execute("""
            UPDATE events
            SET status = 'Reviewed'
            WHERE status = 'In Progress'
        """)

        conn.execute("""
            UPDATE events
            SET status = 'False Positive'
            WHERE status = 'Resolved'
        """)


# ---------------- MACHINE LEARNING ----------------

def classify_log(raw_log):
    prediction = model.predict([raw_log])[0]
    probabilities = model.predict_proba([raw_log])[0]
    confidence = float(max(probabilities))

    return str(prediction), round(confidence, 4)


# ---------------- HELPER FUNCTIONS ----------------

def row_to_dict(row):
    return dict(row)


def require_api_key():
    return bool(API_KEY) and (
        request.headers.get("X-API-Key") == API_KEY
    )


def parse_positive_int(value, default, maximum):
    try:
        number = int(value)

        if number < 1:
            return default

        return min(number, maximum)

    except (TypeError, ValueError):
        return default


def parse_date_filter(value, parameter_name):
    """
    Accept ISO dates and datetimes.

    Examples:
        2026-10-24
        2026-10-24T15:30:00
        2026-10-24T15:30:00+00:00
    """
    if not value:
        return None, None

    try:
        parsed = datetime.fromisoformat(value)

        # Convert timezone-aware dates to UTC.
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc)
            parsed = parsed.replace(tzinfo=None)

        return parsed.isoformat(), None

    except ValueError:
        return None, (
            f"Invalid {parameter_name}. "
            "Use YYYY-MM-DD or an ISO datetime."
        )


# ---------------- HOME AND HEALTH ----------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Raksha SOC API is running",
        "endpoints": [
            "GET /health",
            "POST /events",
            "GET /events",
            "GET /events/<id>",
            "PATCH /events/<id>",
            "GET /stats",
        ],
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


# ---------------- CREATE SECURITY EVENTS ----------------

@app.route("/events", methods=["POST"])
def create_event():
    if not require_api_key():
        return jsonify({
            "error": "Invalid or missing API key"
        }), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required"
        }), 400

    batch = data.get("events")

    if batch is not None:
        if not isinstance(batch, list) or not batch:
            return jsonify({
                "error": "events must be a non-empty list"
            }), 400

        if len(batch) > 100:
            return jsonify({
                "error": "Maximum 100 events per request"
            }), 400

        inputs = batch
    else:
        inputs = [data]

    # Validate all events before inserting any.
    for item in inputs:
        if not isinstance(item, dict):
            return jsonify({
                "error": "Each event must be a JSON object"
            }), 400

        raw_log = item.get("raw_log")
        source = item.get("source", "unknown")

        if not isinstance(raw_log, str) or not raw_log.strip():
            return jsonify({
                "error": "Every event needs a non-empty raw_log"
            }), 400

        if len(raw_log) > 10000:
            return jsonify({
                "error": "raw_log cannot exceed 10000 characters"
            }), 400

        if (
            not isinstance(source, str)
            or not source.strip()
            or len(source) > 200
        ):
            return jsonify({
                "error": (
                    "source must be a non-empty string "
                    "up to 200 characters"
                )
            }), 400

    created_events = []
    conn = get_db()

    try:
        for item in inputs:
            raw_log = item["raw_log"].strip()
            source = item.get("source", "unknown").strip()

            risk_level, confidence = classify_log(raw_log)
            timestamp = datetime.now(timezone.utc).isoformat()

            cursor = conn.execute(
                """
                INSERT INTO events
                (raw_log, source, timestamp, risk_level,
                 confidence, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    raw_log,
                    source,
                    timestamp,
                    risk_level,
                    confidence,
                    "New",
                ),
            )

            created_events.append({
                "id": cursor.lastrowid,
                "raw_log": raw_log,
                "source": source,
                "timestamp": timestamp,
                "risk_level": risk_level,
                "confidence": confidence,
                "status": "New",
            })

        conn.commit()

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while creating events")

        return jsonify({
            "error": "Could not save events"
        }), 500

    finally:
        conn.close()

    if batch is not None:
        return jsonify({
            "message": "Events saved successfully",
            "count": len(created_events),
            "events": created_events,
        }), 201

    return jsonify(created_events[0]), 201


# ---------------- LIST AND FILTER EVENTS ----------------

@app.route("/events", methods=["GET"])
def list_events():
    risk_level = request.args.get("risk_level")
    status = request.args.get("status")
    source = request.args.get("source")

    raw_start_date = request.args.get("start_date")
    raw_end_date = request.args.get("end_date")

    start_date, start_error = parse_date_filter(
        raw_start_date, "start_date"
    )
    end_date, end_error = parse_date_filter(
        raw_end_date, "end_date"
    )

    if start_error:
        return jsonify({"error": start_error}), 400

    if end_error:
        return jsonify({"error": end_error}), 400

    if risk_level and risk_level not in VALID_RISK_LEVELS:
        return jsonify({
            "error": "Invalid risk_level filter"
        }), 400

    if status and status not in VALID_STATUSES:
        return jsonify({
            "error": "Invalid status filter"
        }), 400

    if source is not None and not source.strip():
        return jsonify({
            "error": "source filter cannot be empty"
        }), 400

    # Compare normalized values to catch invalid ranges.
    if start_date and end_date and start_date > end_date:
        return jsonify({
            "error": "start_date must not be after end_date"
        }), 400

    limit = parse_positive_int(
        request.args.get("limit"), 50, 500
    )

    offset = parse_positive_int(
        request.args.get("offset"), 1, 1000000
    ) - 1

    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if risk_level:
        query += " AND risk_level = ?"
        params.append(risk_level)

    if status:
        query += " AND status = ?"
        params.append(status)

    if source:
        query += " AND source = ?"
        params.append(source.strip())

    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)

    if end_date:
        # A date-only end date includes the entire selected day.
        if raw_end_date and len(raw_end_date) == 10:
            next_day = (
                datetime.fromisoformat(raw_end_date) + timedelta(days=1)
            )
            query += " AND timestamp < ?"
            params.append(next_day.isoformat())
        else:
            query += " AND timestamp <= ?"
            params.append(end_date)

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    return jsonify({
        "count": len(rows),
        "events": [row_to_dict(row) for row in rows],
    })


# ---------------- GET ONE EVENT ----------------

@app.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()

    if row is None:
        return jsonify({
            "error": "Event not found"
        }), 404

    return jsonify(row_to_dict(row))


# ---------------- UPDATE EVENT STATUS ----------------

@app.route("/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    if not require_api_key():
        return jsonify({
            "error": "Invalid or missing API key"
        }), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required"
        }), 400

    status = data.get("status")

    if status not in VALID_STATUSES:
        return jsonify({
            "error": (
                "status must be New, Reviewed, "
                "False Positive, or Escalated"
            )
        }), 400

    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE events SET status = ? WHERE id = ?",
            (status, event_id),
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Event not found"
            }), 404

        row = conn.execute(
            "SELECT * FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()

    return jsonify(row_to_dict(row))


# ---------------- STATISTICS ----------------

@app.route("/stats", methods=["GET"])
def get_stats():
    with get_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]

        risk_rows = conn.execute("""
            SELECT risk_level, COUNT(*) AS total
            FROM events
            GROUP BY risk_level
        """).fetchall()

        status_rows = conn.execute("""
            SELECT status, COUNT(*) AS total
            FROM events
            GROUP BY status
        """).fetchall()

        source_rows = conn.execute("""
            SELECT source, COUNT(*) AS total
            FROM events
            GROUP BY source
        """).fetchall()

    risk_counts = {level: 0 for level in VALID_RISK_LEVELS}
    risk_counts.update({
        row["risk_level"]: row["total"]
        for row in risk_rows
    })

    status_counts = {status: 0 for status in VALID_STATUSES}
    status_counts.update({
        row["status"]: row["total"]
        for row in status_rows
    })

    source_counts = {
        row["source"]: row["total"]
        for row in source_rows
    }

    return jsonify({
        "total_events": total,
        "risk_counts": risk_counts,
        "status_counts": status_counts,
        "source_counts": source_counts,
    })


# ---------------- START APPLICATION ----------------

initialize_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
