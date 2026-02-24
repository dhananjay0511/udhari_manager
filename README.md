# Udhari — Credit Ledger Manager

A professional Django web app for tracking personal loans and credit. Multi-user, interest calculation, overdue alerts, and full CRUD.

---

### Step 1 - Create the MySQL database

Open MySQL Workbench or MySQL CLI and run:
```sql
CREATE DATABASE udhari_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 2 - Create your `.env` file

In the project root (same folder as `manage.py`), create a file named `.env`:
```
cp .env.example .env
```

Edit `.env` and fill in your MySQL password:
```
DJANGO_SECRET_KEY=any-long-random-string-here-50-plus-chars
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.mysql
DB_NAME=udhari_db
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
DB_HOST=127.0.0.1
DB_PORT=3306
```

### Step 3 - Install all requirements

```bash
pip install -r requirements.txt
```

> If `mysqlclient` fails to install on Windows, try:
> ```bash
> pip install mysqlclient --only-binary=:all:
> ```
> Or install from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

### Step 4 - Run migrations

```bash
python manage.py migrate
```

You should now see tables in MySQL Workbench under `udhari_db`.

### Step 5 - Create superuser and run

```bash
python manage.py createsuperuser
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## Full Setup from Scratch

```bash
# 1. Extract project and enter folder
cd udhari_manager

# 2. Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env (see above)
cp .env.example .env
# Edit .env with your MySQL credentials

# 5. Create MySQL database
# In MySQL Workbench: CREATE DATABASE udhari_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 6. Migrate
python manage.py migrate

# 7. Create admin account
python manage.py createsuperuser

# 8. Run
python manage.py runserver
```

---

## ✨ Features

| Feature | Details |
|---|---|
| Auth | Register, Login, Logout — session-based |
| People | Add/Edit/Delete contacts with opening balance |
| Transactions | GIVEN / RECEIVED with date, due date, description |
| **Interest** | Simple or Compound — auto-calculated daily |
| Balance | ORM-annotated — no N+1 queries |
| Filters | Search, overdue, has-due-date, sort |
| Overdue Alerts | Visual badges + warning banners |
| Multi-tenant | Complete data isolation per user |
| Admin | Django admin at /admin/ |

---

## 💹 Interest Calculation

When adding a transaction, you can optionally enable interest:

- **Simple Interest**: `I = Principal × Rate × Time(years)`
- **Compound Interest**: Monthly compounding: `A = P × (1 + r/12)^(12t) - P`
- Interest is displayed as accrued-to-today on all views
- The total (principal + interest) is shown in the person detail page

---

## 🌐 Hosting on Railway (Recommended — Free Tier Available)

Railway is the easiest platform. Takes ~10 minutes.

### Step 1 — Push to GitHub

```bash
# In project root
git init
echo "venv/" > .gitignore
echo ".env" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "db.sqlite3" >> .gitignore
echo "staticfiles/" >> .gitignore
git add .
git commit -m "Initial commit"
# Create a repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/udhari-ledger.git
git push -u origin main
```

### Step 2 — Deploy on Railway

1. Go to https://railway.app and sign up (free)
2. Click **"New Project"** → **"Deploy from GitHub"**
3. Select your repo
4. Railway auto-detects Django. Add a **MySQL** service:
   - Click **+ New** → **Database** → **MySQL**
5. In your Django service, go to **Variables** and add:

```
DJANGO_SECRET_KEY=django-insecure-9w$7pLx!3qZ@vR2kT#8mNsY6bHcD4fG1uJ0aX!pQrStUvWxYz
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-app.railway.app
DB_ENGINE=django.db.backends.mysql
DB_NAME=${{MySQL.MYSQLDATABASE}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
DB_HOST=${{MySQL.MYSQLHOST}}
DB_PORT=${{MySQL.MYSQLPORT}}
```

6. Add a **`Procfile`** to your project root:
```
web: gunicorn udhari_manager.wsgi --log-file -
```

7. Add `railway.json` to project root:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": { "builder": "NIXPACKS" },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn udhari_manager.wsgi",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

8. Commit and push — Railway auto-deploys.

9. Create superuser via Railway's **Shell** tab:
```bash
python manage.py createsuperuser
```

10. Your app is live at `https://your-app.railway.app`!

---

## 🌐 Alternative: Render (also free)

1. Push to GitHub (same as above)
2. Go to https://render.com → **New Web Service**
3. Connect your repo
4. Set **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
5. Set **Start Command**: `gunicorn udhari_manager.wsgi`
6. Add a **PostgreSQL** or **MySQL** add-on (or use Railway just for DB)
7. Set environment variables same as above

---

## 🔒 Security Checklist for Production

- [ ] Set `DJANGO_SECRET_KEY` to a random 50+ char string
- [ ] Set `DJANGO_DEBUG=False`
- [ ] Set `DJANGO_ALLOWED_HOSTS` to your domain only
- [ ] Use HTTPS (Railway/Render provide this free)
- [ ] Run `python manage.py collectstatic` before deploying
- [ ] Never commit `.env` to git (it's in `.gitignore`)

---

## 🧪 Running Tests

```bash
python manage.py test ledger accounts
```

Covers: permissions (IDOR protection), balance annotation accuracy, overdue filter logic, form validation, auth flows.

---

## 📁 Project Structure

```
udhari_manager/
├── .env.example          ← Copy to .env and fill credentials
├── .gitignore
├── Procfile              ← For Railway/Render deployment
├── railway.json          ← Railway config
├── manage.py
├── requirements.txt
├── README.md
├── static/css/style.css  ← Professional custom CSS
├── templates/base.html   ← Sidebar layout
├── udhari_manager/       ← Django project config
├── accounts/             ← Auth (register/login/logout)
└── ledger/               ← Core business logic
    ├── models.py         ← Person + Transaction (with interest)
    ├── views.py          ← CBVs, all CRUD
    ├── forms.py          ← ModelForms with validation
    ├── utils.py          ← ORM balance annotation
    └── templates/ledger/ ← All HTML templates
```
