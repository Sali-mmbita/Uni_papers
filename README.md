📚 UniPapers – University Revision Papers Platform

The platform is live on https://cogniprep.onrender.com/
A Flask-based web application for uploading, managing, and accessing university revision papers.
Secure, fast, and fully deployment-ready on Render.

🚀 Features
👥 User System

User registration & login

Email-based password reset (secure token)

Admin dashboard access

Account status controls:

Ban / unban users

Promote / demote users (Admin ⇆ User)

Optional Two-Factor Authentication (2FA) using Google Authenticator

📄 Paper Management

Upload PDF/DOCX revision papers (securely)

File sanitization using secure_filename

Per-user "My Papers" page

Pagination

Search & filter functionality

Delete confirmation modals

🔐 Security & Hardening

2FA with pyotp

CSRF protection via Flask-WTF

Session hardening:

SESSION_COOKIE_SECURE = True

REMEMBER_COOKIE_SECURE = True

File size limits

Allowed extensions validation

☁️ Deployment (Render)

App factory pattern

Production config class

Gunicorn server

PostgreSQL database

Persistent /uploads directory

🏗️ Project Structure
UniPapers/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── email.py
│   ├── extensions.py
│   ├── config.py
│   │
│   ├── auth/
│   │   ├── forms.py
│   │   ├── routes.py
│   │   └── templates/auth/
│   │
│   ├── main/
│   │   ├── forms.py
│   │   ├── routes.py
│   │   └── templates/main/
│   │
│   └── static/
│
├── uploads/
│   └── papers/
│
├── wsgi.py
├── run.py
├── requirements.txt
├── README.md
└── render.yaml

⚙️ Installation Guide (Local Development)
1️⃣ Clone Repository
git clone https://github.com/your-username/UniPapers.git
cd UniPapers

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create .env:

FLASK_ENV=development
SECRET_KEY=your-secret-key
SQLALCHEMY_DATABASE_URI=sqlite:///site.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

5️⃣ Initialize Database
flask db init
flask db migrate -m "initial migration"
flask db upgrade

▶️ Run App (Local)
flask run

🌐 Deployment on Render (Free Tier Compatible)

Render auto-builds using:

requirements.txt

wsgi.py

render.yaml

Key Notes

PostgreSQL is used in production

Uploads stored via Render Persistent Disk

Gunicorn handles production serving

🔑 Admin Access

After deployment, manually create an admin:

Option A: Python Shell (locally)
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    u = User(username="admin", email="admin@example.com", role="admin")
    u.set_password("yourpassword")
    db.session.add(u)
    db.session.commit()

🧪 Technologies Used
Tech	Purpose
Flask	Core web framework
PostgreSQL	Production database
SQLAlchemy	ORM
Flask-Migrate	Database migrations
Flask-Login	Authentication
Flask-Mail	Email verification & password reset
PyOTP	Two-factor authentication
WTForms	Forms & validation
Gunicorn	Production server
Render	Deployment


🧩 Future Improvements

Analytics dashboard

University/department categorization

AI search for papers

Bulk upload for admins

User activity logs

Improved UI/UX theme

Download tracking

📝 License

This project is open for educational and personal use.

❤️ Contribution

Feel free to open issues or pull requests.
