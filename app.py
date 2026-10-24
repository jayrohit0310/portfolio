import os
import json
import logging
import hashlib
import shutil
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv

# Import the chatbot helper
from ai_assistant import ask_jay_bot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base directory determination
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Static folder fallback check
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
if not os.path.exists(STATIC_FOLDER) and os.path.exists(os.path.join(BASE_DIR, 'public', 'static')):
    STATIC_FOLDER = os.path.join(BASE_DIR, 'public', 'static')

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=STATIC_FOLDER,
    static_url_path='/static'
)

# WSGI Middleware to handle Vercel internal URL rewrites seamlessly
class VercelPathFixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path in ('/api/index.py', '/api/index', '/api'):
            orig_uri = environ.get('HTTP_X_FORWARDED_URI') or environ.get('HTTP_X_MATCHED_PATH')
            if orig_uri:
                environ['PATH_INFO'] = orig_uri.split('?')[0]
            else:
                environ['PATH_INFO'] = '/'
        elif path.startswith('/api/index.py/'):
            environ['PATH_INFO'] = path[len('/api/index.py'):]
        elif path.startswith('/api/index/'):
            environ['PATH_INFO'] = path[len('/api/index'):]
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)

# --- DATABASE FALLBACK SYSTEM ---
# Serverless environments (like Vercel) have a read-only filesystem except for /tmp.
is_vercel = os.getenv("VERCEL") is not None or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None

import tempfile

if is_vercel:
    JSON_DB_PATH = os.path.join(tempfile.gettempdir(), 'data_store.json')
    bundled_db = os.path.join(BASE_DIR, 'data_store.json')
    if not os.path.exists(JSON_DB_PATH) and os.path.exists(bundled_db):
        try:
            shutil.copy2(bundled_db, JSON_DB_PATH)
        except Exception as e:
            logger.warning(f"Could not copy bundled data_store.json to temp dir: {e}")
else:
    JSON_DB_PATH = os.path.join(BASE_DIR, 'data_store.json')

def load_json_db():
    if not os.path.exists(JSON_DB_PATH):
        default_data = {
            "visitors": [],
            "messages": [],
            "visitor_count": 0
        }
        try:
            with open(JSON_DB_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4)
        except Exception as e:
            logger.warning(f"Unable to write initial JSON DB to {JSON_DB_PATH}: {e}")
        return default_data
    try:
        with open(JSON_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON DB: {e}")
        return {"visitors": [], "messages": [], "visitor_count": 0}

def save_json_db(data):
    try:
        with open(JSON_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error writing to JSON DB at {JSON_DB_PATH}: {e}")

# Try to connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "")
db_connected = False
db = None
client = None

# On Vercel without external MONGO_URI, skip localhost MongoDB to prevent cold start connection timeout
if is_vercel and (not MONGO_URI or "localhost" in MONGO_URI or "127.0.0.1" in MONGO_URI):
    logger.info("Running on Vercel without external MongoDB. Using JSON database fallback.")
    db_connected = False
else:
    target_uri = MONGO_URI if MONGO_URI else "mongodb://localhost:27017/portfolio"
    try:
        logger.info(f"Connecting to MongoDB at: {target_uri}")
        client = MongoClient(target_uri, serverSelectionTimeoutMS=2000)
        # Trigger connection validation
        client.server_info()
        db = client.get_default_database()
        db_connected = True
        logger.info("Successfully connected to MongoDB!")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Falling back to JSON database file: {JSON_DB_PATH}")
        db_connected = False

# Database operations helpers
def increment_and_get_visitor(ip_address):
    ip_hash = hashlib.sha256(ip_address.encode('utf-8')).hexdigest()
    now_utc = datetime.now(timezone.utc)
    today_str = now_utc.strftime('%Y-%m-%d')
    
    if db_connected and db is not None:
        try:
            # Check if visitor already exists for today
            existing = db.visitors.find_one({"ip_hash": ip_hash, "date": today_str})
            if not existing:
                db.visitors.insert_one({
                    "ip_hash": ip_hash,
                    "date": today_str,
                    "timestamp": now_utc
                })
            # Return total unique visitors (by ip_hash overall or count)
            total_unique = len(db.visitors.distinct("ip_hash"))
            return total_unique
        except Exception as e:
            logger.error(f"MongoDB visitor tracking error: {e}")
            # Fallback to JSON below
    
    # JSON Fallback
    data = load_json_db()
    
    # Check uniqueness
    is_unique_today = not any(v.get("ip_hash") == ip_hash and v.get("date") == today_str for v in data.get("visitors", []))
    if is_unique_today:
        data.setdefault("visitors", []).append({
            "ip_hash": ip_hash,
            "date": today_str,
            "timestamp": now_utc.isoformat()
        })
    
    # Get total unique hashes
    unique_hashes = set(v.get("ip_hash") for v in data.get("visitors", []) if "ip_hash" in v)
    total_unique = max(len(unique_hashes), 1)
    data["visitor_count"] = total_unique
    save_json_db(data)
    return total_unique

def save_contact_message(name, email, message):
    now_utc = datetime.now(timezone.utc)
    msg_data = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": now_utc
    }
    
    if db_connected and db is not None:
        try:
            db.messages.insert_one(msg_data)
            logger.info(f"Saved contact message in MongoDB from {email}")
            return True
        except Exception as e:
            logger.error(f"MongoDB contact message save error: {e}")
            # Fallback to JSON below
            
    # JSON Fallback
    data = load_json_db()
    json_entry = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": now_utc.isoformat()
    }
    data.setdefault("messages", []).append(json_entry)
    save_json_db(data)
    logger.info(f"Saved contact message in JSON file from {email}")
    return True

# --- FLASK ROUTES ---

@app.route('/')
def home():
    # Track visitor
    ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
    # Clean proxy IP lists if present
    if ip_addr and ',' in ip_addr:
        ip_addr = ip_addr.split(',')[0].strip()
    if not ip_addr:
        ip_addr = "127.0.0.1"
    
    try:
        visitor_count = increment_and_get_visitor(ip_addr)
    except Exception as e:
        logger.error(f"Error in visitor tracking: {e}")
        visitor_count = 1
        
    return render_template('index.html', visitor_count=visitor_count)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "mongodb" if db_connected else "json_fallback"
    })

@app.route('/api/visitor-count', methods=['GET'])
def get_visitor_count():
    if db_connected and db is not None:
        try:
            count = len(db.visitors.distinct("ip_hash"))
            return jsonify({"success": True, "count": count})
        except Exception as e:
            logger.error(e)
            
    # JSON Fallback
    data = load_json_db()
    unique_hashes = set(v.get("ip_hash") for v in data.get("visitors", []) if "ip_hash" in v)
    return jsonify({"success": True, "count": max(len(unique_hashes), 1)})

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        message = data.get("message", "").strip()
        
        if not name or not email or not message:
            return jsonify({"success": False, "error": "Name, email, and message are required"}), 400
            
        save_contact_message(name, email, message)
        
        # Email Alert Notification (Optional)
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        if smtp_user and smtp_password:
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                receiver = os.getenv("RECEIVER_EMAIL", smtp_user)
                smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
                smtp_port = int(os.getenv("SMTP_PORT", "587"))
                
                msg = MIMEMultipart()
                msg['From'] = smtp_user
                msg['To'] = receiver
                msg['Subject'] = f"Portfolio Contact Form: {name}"
                
                body = f"You received a new message from your portfolio contact form:\n\nName: {name}\nEmail: {email}\nMessage:\n{message}"
                msg.attach(MIMEText(body, 'plain'))
                
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                server.quit()
                logger.info("Notification email sent successfully!")
            except Exception as mail_err:
                logger.error(f"Failed to send email alert: {mail_err}")
                
        return jsonify({"success": True, "message": "Your message was sent successfully!"})
    except Exception as e:
        logger.error(f"Contact form processing error: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred"}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"success": False, "error": "Message is required"}), 400
            
        user_message = data.get("message", "")
        response_message = ask_jay_bot(user_message)
        
        return jsonify({
            "success": True, 
            "reply": response_message
        })
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred"}), 500

@app.route('/api/coding-stats', methods=['GET'])
def get_coding_stats():
    # Structured stats for Jay Rohit
    stats = {
        "leetcode": {
            "solved": 248,
            "easy": 98,
            "medium": 130,
            "hard": 20,
            "rank": "Top 12%"
        },
        "hackerrank": {
            "problem_solving_stars": 5,
            "python_stars": 5,
            "badges": ["Problem Solving", "Python", "SQL"]
        },
        "codechef": {
            "stars": "3-Star",
            "rating": 1612,
            "global_rank": 14500
        },
        "codeforces": {
            "rank": "Pupil",
            "rating": 1245,
            "max_rating": 1280
        }
    }
    return jsonify({"success": True, "stats": stats})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    logger.info(f"Starting portfolio app on port {port} in {'debug' if debug else 'production'} mode...")
    app.run(host='0.0.0.0', port=port, debug=debug)
