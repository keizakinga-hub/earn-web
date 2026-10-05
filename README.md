# Arcade, Freelance & Betting Platform

A full-stack Flask web application integrating arcade mini-games (including an Aviator multiplier game), a user referral system, a freelancing portal, and dynamic wallet balance management.

## 🚀 Features

- **Authentication System**: User registration with auto-generated referral codes and encrypted passwords using `Werkzeug`.
- **Referral Tracking**: Rewards users when new accounts sign up using their unique referral link/code.
- **Aviator Mini-Game**: Real-time multiplier crash algorithm simulating bets, win conditions, and live payouts.
- **Freelance Board**: Task listing engine where users can discover and accept micro-jobs.
- **Wallet & Funds**: In-app balance system supporting deposits and transaction tracking.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript (ES6+ Fetch API)
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Deployment**: Render / Gunicorn WSGI

---

## 📦 Local Setup Instructions

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/arcade-freelance-platform.git](https://github.com/YOUR_USERNAME/arcade-freelance-platform.git)
cd arcade-freelance-platform
