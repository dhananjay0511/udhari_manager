Udhari Manager – Ledger & Due Tracking System

A full-stack web application built with Django to digitally manage customer dues, payments, and running balances for small businesses.

🚀 Project Overview

Udhari Manager is a ledger management system designed to replace manual bookkeeping used by small shop owners.
It enables structured tracking of credit transactions, payments, and automatically calculates customer balances in real time.

The application demonstrates backend logic design, database modeling, and financial transaction handling using Django.

🔧 Key Features

Customer management (Add, update, delete)

Record credit (due) transactions

Record payment entries

Automatic balance calculation using transaction logic

Individual customer ledger view

Date-wise transaction tracking

Admin panel for secure data management

🏗 Technical Implementation

Designed relational database schema using Django ORM

Implemented transaction-based balance calculation logic

Structured project using MVC architecture (Django MVT pattern)

Used Django Admin for backend data management

Built clean UI using HTML/CSS templates

🛠 Tech Stack

Backend: Django

Database: SQLite

Language: Python

Frontend: HTML, CSS

⚙️ Installation & Setup
Clone the repository
git clone https://github.com/yourusername/udhari-manager.git
cd udhari-manager
Create and activate virtual environment
python -m venv venv

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate
Install dependencies
pip install -r requirements.txt
Run migrations
python manage.py migrate
Create admin user
python manage.py createsuperuser
Start server
python manage.py runserver

Visit:
http://127.0.0.1:8000/

📌 What This Project Demonstrates

Backend development using Django

Database design and modeling

Financial data handling logic

CRUD operations

Clean project structuring

Understanding of real-world business workflows

🔮 Future Enhancements

REST API integration

PDF export of ledgers

Role-based access control

Deployment on cloud (AWS / Render / Railway)

Dashboard analytics

📄 License

MIT License
