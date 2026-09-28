# 🚀 Live Deployment Guide - Mental Health AI Companion

This guide explains how to deploy your **Mental Health AI Companion** web application to the cloud for free so anyone can use it online.

---

## 🛠 Prerequisites Checklist

1. A **GitHub** account ([github.com](https://github.com)).
2. **Git** installed on your computer.
3. This project folder with all updated files:
   - `app.py`
   - `database_setup.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `.gitignore`
   - `templates/`

---

## 🌟 Method 1: Deploy on Render.com + Free Cloud MySQL (Recommended)

Render offers free web app hosting, and you can pair it with a free cloud MySQL provider (such as **Aiven**, **TiDB Cloud**, or **Clever Cloud**).

### Step 1: Create a Free Cloud MySQL Database

1. Go to [aiven.io](https://aiven.io) or [tidbcloud.com](https://tidbcloud.com) or [clever-cloud.com](https://www.clever-cloud.com).
2. Sign up and create a new **MySQL** service on the free tier.
3. Once created, note down your connection credentials:
   - **Host** (e.g., `mysql-xxxx.aivencloud.com`)
   - **Port** (e.g., `12345`)
   - **User** (e.g., `avnadmin` or `root`)
   - **Password**
   - **Database Name** (e.g., `defaultdb` or `mental_wellness_db`)

### Step 2: Initialize Database Tables on the Cloud Database

On your computer, run `database_setup.py` pointing to the cloud database once:

```powershell
# Set cloud DB variables in your local terminal (or edit your local .env temporarily)
$env:DB_HOST="YOUR_CLOUD_HOST"
$env:DB_PORT="YOUR_CLOUD_PORT"
$env:DB_USER="YOUR_CLOUD_USER"
$env:DB_PASSWORD="YOUR_CLOUD_PASSWORD"
$env:DB_NAME="YOUR_CLOUD_DB_NAME"

# Run setup
python database_setup.py
```

It will create all 19 tables and seed initial support groups and community categories automatically!

---

### Step 3: Push Your Code to GitHub

1. Open a terminal in this project folder:
   ```bash
   git init
   git add .
   git commit -m "Mental Health AI Companion ready for production"
   ```
2. Create a new repository on [GitHub](https://github.com/new) named `mental-health-ai`.
3. Push your repository:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/mental-health-ai.git
   git branch -M main
   git push -u origin main
   ```

*(Note: `.gitignore` protects your `.env` file so your private passwords are never exposed publicly on GitHub!)*

---

### Step 4: Deploy on Render

1. Go to [render.com](https://render.com) and log in with your GitHub account.
2. Click **New +** -> **Web Service**.
3. Select your GitHub repository (`mental-health-ai`).
4. Configure the service:
   - **Name:** `mental-health-ai`
   - **Environment:** `Python 3`
   - **Region:** Closest to you (e.g., Singapore, Frankfurt, Oregon)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`
5. Click **Environment Variables** (or "Advanced") and add the following:
   | Key | Value |
   | :--- | :--- |
   | `DB_HOST` | *(Your cloud MySQL host)* |
   | `DB_PORT` | *(Your cloud MySQL port, e.g. 3306 or provider port)* |
   | `DB_USER` | *(Your cloud MySQL user)* |
   | `DB_PASSWORD` | *(Your cloud MySQL password)* |
   | `DB_NAME` | *(Your cloud MySQL database name)* |
   | `SECRET_KEY` | *(A random secure string for user sessions)* |
   | `GEMINI_API_KEY` | *(Optional: your Google Gemini API key for AI chat)* |
6. Click **Create Web Service**.
7. Render will build and deploy your app. In 2–3 minutes, you will receive a live URL (e.g., `https://mental-health-ai.onrender.com`)!

---

## 🌟 Method 2: Deploy on PythonAnywhere (Free & Includes MySQL)

[PythonAnywhere.com](https://www.pythonanywhere.com) is one of the simplest free hosts because it includes both Python web hosting and a MySQL database built right in:

1. Sign up for a free account at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Go to the **Databases** tab:
   - Set a MySQL password.
   - Click **Create database** (e.g., `username$mental_wellness_db`).
3. Go to the **Consoles** tab -> **Bash**:
   - Clone your GitHub repository:
     ```bash
     git clone https://github.com/YOUR_USERNAME/mental-health-ai.git
     cd mental-health-ai
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```
   - Run `python database_setup.py` (after creating `.env` with your PythonAnywhere MySQL credentials).
4. Go to the **Web** tab:
   - Click **Add a new web app** -> **Manual configuration** -> **Python 3.10 / 3.11**.
   - Set **Virtualenv** to `/home/YOUR_USERNAME/mental-health-ai/venv`.
   - In the **WSGI configuration file**, point to your `app.py`:
     ```python
     import sys
     path = '/home/YOUR_USERNAME/mental-health-ai'
     if path not in sys.path:
         sys.path.append(path)

     from app import app as application
     ```
   - Click **Reload**. Your site is now live at `https://YOUR_USERNAME.pythonanywhere.com`!

---

## 🌟 Method 3: Deploy on Railway.app

1. Go to [railway.app](https://railway.app).
2. Click **New Project** -> **Provision MySQL**.
3. In the same project, click **New** -> **GitHub Repo** and connect your repository.
4. In the Web Service settings, link the MySQL service environment variables (`MYSQLHOST`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`, `MYSQLPORT`).
5. Railway will automatically build and deploy the app!

---

## ✅ Post-Deployment Verification

Once deployed, visit your live URL and test:
1. Open homepage: verify images, styling, and navigation load cleanly.
2. Click **Talk to AI Companion** or the floating button at bottom-right to test interactive AI chat.
3. Click **Register** to create a test user account.
4. Test logging a mood in **Mood Tracker** and an entry in **Journaling**.
5. Visit **Settings** to update your display name and check your profile stats.
