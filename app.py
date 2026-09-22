import os
import json
import logging
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Import the chatbot helper
from ai_assistant import ask_jay_bot

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- DATABASE FALLBACK SYSTEM ---
# If MongoDB is not running, we write to a local JSON file: data_store.json
JSON_DB_PATH = os.path.join(os.path.dirname(__file__), 'data_store.json')

def load_json_db():
    if not os.path.exists(JSON_DB_PATH):
        default_data = {
            "visitors": [],
            "messages": [],
            "visitor_count": 0
        }
        with open(JSON_DB_PATH, 'w') as f:
            json.dump(default_data, f, indent=4)
        return default_data
    try:
        with open(JSON_DB_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON DB: {e}")
        return {"visitors": [], "messages": [], "visitor_count": 0}

def save_json_db(data):
    try:
        with open(JSON_DB_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error writing to JSON DB: {e}")

# Try to connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/portfolio")
db_connected = False
db = None
client = None

try:
    logger.info(f"Connecting to MongoDB at: {MONGO_URI}")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    # Trigger connection validation
    client.server_info()
    db = client.get_default_database()
    db_connected = True
    logger.info("Successfully connected to MongoDB!")
except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
    logger.warning(f"MongoDB connection failed: {e}. Falling back to JSON database file: {JSON_DB_PATH}")
    db_connected = False

# Database operations helpers
def increment_and_get_visitor(ip_address):
    ip_hash = hashlib.sha256(ip_address.encode('utf-8')).hexdigest()
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    
    if db_connected:
        try:
            # Check if visitor already exists for today
            existing = db.visitors.find_one({"ip_hash": ip_hash, "date": today_str})
            if not existing:
                db.visitors.insert_one({
                    "ip_hash": ip_hash,
                    "date": today_str,
                    "timestamp": datetime.utcnow()
                })
            # Return total unique visitors (by ip_hash overall or count)
            total_unique = len(db.visitors.distinct("ip_hash"))
            return total_unique
        except Exception as e:
            logger.error(f"MongoDB visitor tracking error: {e}")
            # Fallback to JSON below
    
    # JSON Fallback
    data = load_json_db()
    visitor_entry = {"ip_hash": ip_hash, "date": today_str}
    
    # Check uniqueness
    is_unique_today = not any(v["ip_hash"] == ip_hash and v["date"] == today_str for v in data["visitors"])
    if is_unique_today:
        data["visitors"].append({
            "ip_hash": ip_hash,
            "date": today_str,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    # Get total unique hashes
    unique_hashes = set(v["ip_hash"] for v in data["visitors"])
    total_unique = len(unique_hashes)
    data["visitor_count"] = total_unique
    save_json_db(data)
    return total_unique

def save_contact_message(name, email, message):
    msg_data = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    
    if db_connected:
        try:
            db.messages.insert_one(msg_data)
            logger.info(f"Saved contact message in MongoDB from {email}")
            return True
        except Exception as e:
            logger.error(f"MongoDB contact message save error: {e}")
            # Fallback to JSON below
            
    # JSON Fallback
    data = load_json_db()
    msg_data["timestamp"] = msg_data["timestamp"].isoformat()
    data["messages"].append(msg_data)
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
    
    try:
        visitor_count = increment_and_get_visitor(ip_addr)
    except Exception as e:
        logger.error(f"Error in visitor tracking: {e}")
        visitor_count = 1
        
    return render_template('index.html', visitor_count=visitor_count)

@app.route('/api/visitor-count', methods=['GET'])
def get_visitor_count():
    if db_connected:
        try:
            count = len(db.visitors.distinct("ip_hash"))
            return jsonify({"success": True, "count": count})
        except Exception as e:
            logger.error(e)
            
    # JSON Fallback
    data = load_json_db()
    unique_hashes = set(v["ip_hash"] for v in data["visitors"])
    return jsonify({"success": True, "count": len(unique_hashes)})

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
        
        # Email Alert Simulation / Integration
        # We can implement a clean SMTP sender here. If settings are empty, we just skip it.
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
    # Return mock but realistic stats for Jay Rohit
    # In a full production application, this endpoint could fetch and cache statistics from LeetCode / Codeforces APIs
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
