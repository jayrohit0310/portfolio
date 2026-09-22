# Jay Rohit - Personal Portfolio Website

A premium, modern, responsive, and recruiter-friendly personal portfolio website built with a lightweight Python stack of **Flask** and **MongoDB** on the backend, styled with **Tailwind CSS** and customized interactions on the frontend.

## ✨ Features

- **Futuristic & Recruiter-Friendly Design**: Stunning neon/indigo gradients, clean layout, custom scrollbar, and glassmorphic cards.
- **Custom Particles Canvas**: An interactive HTML5 Canvas background that connects particle nodes on hover and dynamically adjusts colors on theme changes. Persists settings without lagging.
- **Dark/Light Mode**: Smooth theme transition toggler with preference persistence in `localStorage`.
- **Dynamic Typing Text**: Auto-typing animation displaying different professional roles (IT Student, Python Developer, Web Developer, Problem Solver) in the Hero section.
- **Custom Easing Cursor**: Custom trailing cursor dot and ring which expands on hovering interactive components (buttons, links, form inputs). Toggles off on mobile devices automatically.
- **Floating AI Assistant (Ask Jay Bot)**: Integrated chatbot widget with suggestion chips ("Skills", "Projects", "Contact"). Runs a smart, zero-cost keyword-weight matching QA system in Python.
- **Interactive Project Filtering**: Category filtering (All, Python, Web, AI) that dynamically transitions project cards.
- **Coding Profiles & Cached Stats**: Integrates LeetCode, HackerRank, CodeChef, and Codeforces metrics via a backend API endpoint `/api/coding-stats`.
- **Mock Commit Matrix**: An interactive contribution grid mimicking GitHub’s green commit board.
- **Robust Visitor Counter**: Tracks unique visitor counts based on SHA256 hashed IP logs.
- **Contact Form Validation**: Form submission via AJAX to `/api/contact` which logs submissions in the database, displays inline success alert status, and triggers SMTP email alerts if configured.
- **No-Database Fallback**: If a MongoDB database server isn't running or reachable, the application automatically falls back to storing message lists and visitor logs in a local `data_store.json` file. **The app is guaranteed to run out-of-the-box!**

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Tailwind CSS (via stable CDN v3), FontAwesome Icons, Custom JS
- **Backend**: Flask (Python)
- **Database**: MongoDB (or automatic JSON-file fallback)
- **Dependencies**: `flask`, `pymongo`, `python-dotenv`, `requests`

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or above installed on your system.
- *(Optional)* MongoDB running locally or a MongoDB Atlas cloud URI.

### Installation

1. Clone or copy this repository to your local machine.
2. Open your terminal in the project directory:
   ```bash
   cd "Personal Portfolio"
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a copy of `.env.example` named `.env` and configure your settings:
```bash
cp .env.example .env
```
Inside `.env`, you can customize:
- `MONGO_URI`: The connection link to your MongoDB database (defaults to local `mongodb://localhost:27017/portfolio`).
- `PORT`: Server port (default is 5000).
- `SMTP_USER` & `SMTP_PASSWORD`: If you want the contact form to forward submissions to your personal email inbox.

### Running the Application

Start the Flask development server:
```bash
python app.py
```
You will see output similar to:
```text
 * Serving Flask app 'app.py'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```
Open [http://localhost:5000](http://localhost:5000) in your web browser to view the portfolio.

---

## 📂 Project Structure

```text
Personal Portfolio/
├── app.py                  # Main Flask web application and API routing
├── ai_assistant.py         # Chatbot QA search logic & knowledge base
├── requirements.txt        # Python library requirements
├── .env.example            # Environment variables configuration template
├── static/
│   ├── css/
│   │   └── style.css       # Custom stylesheets (cursor, scrollbars, canvas)
│   ├── js/
│   │   ├── main.js         # Theme toggle, cursor, scroll animations, stats fetching
│   │   ├── particles.js    # Canvas particle system background
│   │   └── chat.js         # Chatbot AJAX messaging UI interaction
│   └── images/
│       └── profile.png     # Professional developer avatar
└── templates/
    └── index.html          # Main HTML structure & Tailwind layouts
```

---

## 🧪 API Endpoints

- `GET /`: Serves the primary single-page HTML layout.
- `GET /api/visitor-count`: Returns the total unique visitor count.
- `POST /api/chat`: Processes user chatbot inputs and returns structured answers.
  - Request body: `{"message": "string"}`
- `POST /api/contact`: Saves user messages and attempts email forwarding.
  - Request body: `{"name": "string", "email": "string", "message": "string"}`
- `GET /api/coding-stats`: Returns LeetCode, HackerRank, CodeChef, and Codeforces user statistics.
