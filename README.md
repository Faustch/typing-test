# Typing Speed Test Web Application

A full-stack typing speed test web application inspired by Monkeytype.  
Built with **Flask**, **MongoDB Atlas**, **Flask-Login**, and **Authlib** for OAuth.  
Users can take typing tests, view their typing history, and track personal statistics.

### Vercel Links:
https://typing-test-delta-three.vercel.app/
https://typing-test-glyphiis-projects.vercel.app/
---

## 🚀 Features

### 🧪 Typing Test
- Time mode (15s / 30s / 60s)  
- Word count mode (25 / 50 / 100 words)  
- Automatic start when typing begins  
- Live stats:
  - Words per minute (WPM)
  - Accuracy
  - Errors
  - Backspaces
- **Press Enter to submit early**
- Results summary shown at the end
- Saves results for logged-in users

### 👤 User Accounts
- Register / Login using Flask-Login
- Secure password hashing
- (Optional) Google OAuth authentication via Authlib
- User session management

### 📊 History & Dashboard
- View a full list of all past tests
- Dashboard includes:
  - Average WPM
  - Best WPM
  - Total number of tests
  - Average accuracy

### 🗄️ MongoDB Atlas Backend
- `users` collection  
- `tests` collection  
- Stores typing test metrics & timestamps

---

## 🧰 Tech Stack

### Backend
- Python 3.13
- Flask
- Flask-Login
- Flask-WTF
- Authlib (for Google OAuth)
- Flask-PyMongo
- MongoDB Atlas

### Frontend
- HTML / CSS (Jinja2 templates)
- Vanilla JavaScript for:
  - Timer
  - Real-time stats
  - Test submission
  - Input tracking

---

## Create an virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
```
## Install Dependencies
```bash
pip install -r requirements.txt
```

## create a .env file
```
SECRET_KEY=your-secret-key
MONGO_URI=your-mongodb-atlas-uri
GOOGLE_CLIENT_ID=your-google-client-id   # optional
GOOGLE_CLIENT_SECRET=your-google-secret  # optional
```

## run the development server
```bash
export FLASK_APP=run.py
flask run
```

