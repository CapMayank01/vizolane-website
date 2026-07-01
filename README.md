# Vizolane Technologies LLP

AI-Powered Smart City Infrastructure & Digital Innovation

## About Vizolane

Vizolane Technologies LLP develops intelligent solutions for smarter cities and modern businesses. Our mission is to leverage AI, automation, and digital technologies to solve real-world urban and business challenges.

### Core Focus Areas

* Intelligent Traffic Management Systems
* Smart Tolling Solutions
* AI-Based Urban Infrastructure
* Web Development
* Digital Transformation
* Data Analytics

---

## Website Features

* Modern responsive design
* Mobile-friendly interface
* Founder portfolio integration
* SEO-optimized structure
* Fast loading performance
* Interactive user experience

---

## Technologies Used

* HTML5 / CSS3 / JavaScript
* Flask (Python)
* Google Sheets API (Contact Logs)
* Gmail SMTP (Email Notifications)
* Vercel Serverless Functions

---

## Project Structure

```
vizolane-website/
├── api/
│   ├── index.py              # Flask backend entry point (Vercel serverless)
│   └── services/
│       ├── email_service.py   # Admin & User email notifications
│       └── sheets_service.py  # Google Sheets form logs
├── static/
│   ├── css/                  # Stylesheets
│   ├── js/                   # Javascript logic
│   └── images/               # Image assets (hero, profile, logo)
├── templates/
│   ├── index.html            # Main home page template
│   ├── founder.html          # Piyush Goel's portfolio template
│   ├── update_portfolio.html # Vithika Goel's portfolio template
│   ├── adminEmail.html       # Email notification body
│   └── userConfirmation.html # User verification template
├── README.md                 # Project documentation
├── requirements.txt          # Python package requirements
├── vercel.json               # Vercel deployment configuration
└── .gitignore                # Untracked files patterns
```

---

## Local Development Setup

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   PORT=3000
   GMAIL_USER=your_gmail@gmail.com
   GMAIL_APP_PASSWORD=your_app_specific_password
   ADMIN_EMAIL=admin_notification_recipient@example.com
   GOOGLE_SHEET_ID=your_google_sheet_id
   GOOGLE_CREDENTIALS_PATH=./credentials.json
   ```

3. **Google Sheets Credentials:**
   Place your service account credentials file in the root directory as `credentials.json` (or set `GOOGLE_CREDENTIALS_PATH` in `.env`).

4. **Run the App:**
   ```bash
   python api/index.py
   ```
   The website will be available at `http://localhost:3000`.

---

© 2026 Vizolane Technologies LLP. All Rights Reserved.
