import re

# Structured knowledge base about Jay Rohit
KNOWLEDGE_BASE = {
    "greeting": (
        "Hello! I am Jay's AI Assistant. Ask me anything about Jay's skills, "
        "projects, achievements, education, coding profiles, or how to contact him!"
    ),
    "about": (
        "Jay Rohit is a B.Tech IT student, Python Developer, Web Developer, and "
        "Passionate about combining "
        "coding and mathematics to solve complex problems and build modern web applications."
    ),
    "skills": (
        "Jay's technical skills are categorized as follows:\n\n"
        "• **Programming**: C++, Python, JavaScript\n"
        "• **Frontend**: HTML5, CSS3, React, Next.js, Tailwind CSS\n"
        "• **Backend**: Flask, FastAPI, Node.js\n"
        "• **Databases**: MongoDB, PostgreSQL, MySQL\n"
        "• **Tools**: Git, GitHub, VS Code, Docker"
    ),
    "projects": (
        "Here are Jay's key projects:\n\n"
        "1. **Math+AI Learning Platform**: A modern web platform combining math problem solving with AI assistance.\n"
        "2. **Stock Portfolio Tracker**: A Python/Flask app to track stock prices and manage portfolios with real-time updates.\n"
        "3. **Restaurant Order System**: A desktop application built with Python to manage billing and orders.\n"
        "4. **Python Automation Scripts**: A collection of scripts automating file management, scraping, and routine tasks.\n"
        "5. **Rule-Based Chatbot**: A smart assistant built with Python NLP rules to answer customer inquiries."
    ),
    "achievements": (
        "Jay's notable achievements include:\n\n"
        ""
        "• **Problem Solving**: Solved 300+ coding challenges across LeetCode, HackerRank, CodeChef, and Codeforces.\n"
        "• **Community Building**: Created an interactive community of math and tech enthusiasts.\n"
        "• **Quiz Creator**: Developed dozens of viral educational quizzes."
    ),
    "education": (
        "Jay is currently pursuing a **Bachelor of Technology (B.Tech) in Information Technology**.\n"
        "His academic progress focuses on Data Structures, Algorithms, Web Development, Database Management, and Mathematics."
    ),
    "contact": (
        "You can connect with Jay Rohit via:\n\n"
        "• **Email**: (Please fill the contact form below or reach out directly!)\n"
        "• **LinkedIn**: https://www.linkedin.com/in/jay-rohit-8204ab320?utm_source=share_via&utm_content=profile&utm_medium=member_android\n"
        "• **GitHub**: https://github.com/jayrohit0310\n"
        ""
        "• **WhatsApp**: Available upon request via the contact form."
    ),
    "brand": (
        ""
        "mental math tricks, coding challenges, and interactive math quizzes to make learning engaging."
    ),
    "python": (
        "Jay has extensive experience with Python! He uses it for backend development (Flask/FastAPI), "
        "writing automation scripts, building CLI tools, and implementing rule-based chatbot systems."
    ),
    "web": (
        "As a Web Developer, Jay works with HTML, CSS, JavaScript, React, Next.js, and Tailwind CSS "
        "on the frontend, and Flask, FastAPI, and Node.js on the backend, integrated with MongoDB and SQL databases."
    ),
    "math": (
        "Mathematics is one of Jay's core passions. He creates math quizzes, "
        "and is highly interested in the intersection of Mathematics, AI, and computer science algorithms."
    ),
    "leetcode": (
        "Jay is active on coding platforms. He solves Data Structures & Algorithms problems on LeetCode "
        "and regularly participates in HackerRank, CodeChef, and Codeforces challenges."
    ),
    "resume": (
        "You can download Jay's resume directly from the Hero section of this website. "
        "It includes a detailed breakdown of his B.Tech progress, technical projects, and certifications."
    )
}

# Mapping of keywords to knowledge base topics
KEYWORD_MAPPING = {
    r"\b(hi|hello|hey|greetings|hola)\b": "greeting",
    r"\b(who are you|about|bio|profile|intro|introduction|jay|rohit)\b": "about",
    r"\b(skill|skills|languages|technologies|stack|frameworks|tools|cpp|c\+\+|javascript|react|nextjs|tailwind|databases|mysql|postgresql|node)\b": "skills",
    r"\b(project|projects|portfolio|apps|restaurant|stock|tracker|learning|chatbot|automation|script|scripts)\b": "projects",
    r"\b(achievement|achievements|awards|accomplishments|solved|challenges|growth|followers)\b": "achievements",
    r"\b(education|college|university|btech|b\.tech|student|it|course|degree|cgpa|academic)\b": "education",
    r"\b(contact|email|phone|linkedin|github|instagram|social|socials|reach|message|whatsapp)\b": "contact",
    r"\b(maths|puzzles|quiz|quizzes)\b": "brand",
    r"\b(python|flask|fastapi|django)\b": "python",
    r"\b(web|frontend|backend|html|css|js|react|next)\b": "web",
    r"\b(math|mathematics|calculus|algebra|geometry)\b": "math",
    r"\b(leetcode|hackerrank|codechef|codeforces|coding|dsa|problem solving|structures|algorithms)\b": "leetcode",
    r"\b(resume|cv|hired|hire|internship|job|work)\b": "resume"
}

def ask_jay_bot(query: str) -> str:
    """
    Answers user queries about Jay Rohit using keyword matching and scoring.
    """
    query = query.lower().strip()
    
    # Track scores for each topic based on matching keywords
    scores = {topic: 0 for topic in KNOWLEDGE_BASE.keys()}
    
    for pattern, topic in KEYWORD_MAPPING.items():
        matches = re.findall(pattern, query)
        if matches:
            scores[topic] += len(matches)
            
    # Find the topic with the highest score
    best_topic = max(scores, key=scores.get)
    
    if scores[best_topic] > 0:
        return KNOWLEDGE_BASE[best_topic]
        
    # Default response if no keywords matched
    return (
        "I'm not sure I understand that question completely. I can tell you about Jay's "
        "**skills**, **projects**, **education**, **achievements**, "
        "**coding profiles** (like LeetCode), or how to **contact** him. What would you like to know?"
    )
