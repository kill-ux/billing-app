# server.py
import os
import threading
import time
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

import logging
from waitress import serve
from paste.translogger import TransLogger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

from app.orders import Base, Order
from app.consume_queue import consume_and_store_order

app = Flask(__name__)

BILLING_DB_USER = os.getenv("BILLING_DB_USER")
BILLING_DB_PASSWORD = os.getenv("BILLING_DB_PASS")
BILLING_DB_NAME = os.getenv("BILLING_DB_NAME")
BILLING_APP_PORT = os.getenv("BILLING_APP_PORT")
BILLING_DB_HOST = os.getenv("BILLING_DB_HOST")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{BILLING_DB_USER}:{BILLING_DB_PASSWORD}@{BILLING_DB_HOST}:5432/{BILLING_DB_NAME}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app, model_class=Base)

# --- Start of Database Resilience Loop ---
def init_app_services(app, db):
    with app.app_context():
        retry_delay = 3
        while True:
            try:
                print("[*] Attempting to connect to the database and verify tables...", flush=True)
                db.create_all()
                print("[*] Database tables verified/created successfully.", flush=True)
                
                consumer_thread = threading.Thread(
                    target=consume_and_store_order, 
                    args=(app, db), 
                    daemon=True
                )
                consumer_thread.start()
                print("[*] RabbitMQ background consumer thread started.", flush=True)
                break
            except Exception as e:
                print(f"[-] Setup notice: {e}. Retrying...", flush=True)
                time.sleep(retry_delay)
# --- End of Database Resilience Loop ---

@app.route('/api/billing/check', methods = ["GET"])
def check():
    return {"status": "ok", "version": "v1.1.1"}, 200
    

@app.route('/api/billing', methods=['GET'])
def get_orders():
    try:
        all_orders = db.session.execute(db.select(Order)).scalars().all()
        
        orders_list = [
            {
                "id": o.id,
                "user_id": o.user_id,
                "number_of_items": o.number_of_items,
                "total_amount": o.total_amount
            } for o in all_orders
        ]
        return jsonify({"status": "success", "data": orders_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

SERVICE_UNAVAILABLE_CODE = 503


@app.route("/health", methods=["GET"])
def health_check():
    health_status = {"status": "ok", "services": {"database": "down"}}
    try:
        db.session.execute(text("SELECT 1"))
        health_status["services"]["database"] = "up"
        status_code = 200
    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        status_code = SERVICE_UNAVAILABLE_CODE
    return health_status, status_code


if __name__ == '__main__':
    logged_app = TransLogger(app, setup_console_handler=True)

    logging.info(f"Starting Waitress server on 0.0.0.0:{BILLING_APP_PORT}...")
    
    init_app_services(app, db)
    
    serve(
        logged_app,
        host='0.0.0.0',
        port=int(BILLING_APP_PORT),
        threads=8
    )