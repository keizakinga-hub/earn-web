import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'arcade-platform-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///platform.db')
# Handle Render PostgreSQL URI prefix compatibility if using Postgres
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Database Models ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(10), unique=True, nullable=False)
    referred_by = db.Column(db.String(10), nullable=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    payout = db.Column(db.Float, nullable=False)

def generate_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Application Routes ---

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    ref_by = request.form.get('referral_code')

    if User.query.filter_by(username=username).first():
        flash('Username already exists. Please pick another one.', 'error')
        return redirect(url_for('home'))

    hashed_pw = generate_password_hash(password)
    new_user = User(
        username=username,
        password_hash=hashed_pw,
        referral_code=generate_ref_code(),
        referred_by=ref_by if ref_by else None
    )

    # Referral bonus reward logic
    if ref_by:
        referrer = User.query.filter_by(referral_code=ref_by).first()
        if referrer:
            referrer.balance += 5.0  # $5 bonus credit to referrer

    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for('dashboard'))

    flash('Invalid username or password.', 'error')
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.all()
    return render_template('dashboard.html', user=current_user, jobs=jobs)

# --- API Endpoints ---

@app.route('/api/deposit', methods=['POST'])
@login_required
def deposit():
    data = request.get_json() or {}
    amount = float(data.get('amount', 0))
    if amount > 0:
        current_user.balance += amount
        db.session.commit()
        return jsonify({'success': True, 'new_balance': current_user.balance})
    return jsonify({'success': False, 'message': 'Invalid deposit amount.'}), 400

@app.route('/api/play-aviator', methods=['POST'])
@login_required
def play_aviator():
    data = request.get_json() or {}
    bet_amount = float(data.get('bet', 0))
    cashout_multiplier = float(data.get('cashout', 1.0))

    if bet_amount <= 0:
        return jsonify({'error': 'Please enter a valid bet amount.'}), 400

    if current_user.balance < bet_amount:
        return jsonify({'error': 'Insufficient wallet balance.'}), 400

    # Deduct bet amount upfront
    current_user.balance -= bet_amount

    # Aviator crash multiplier simulator (weighted range)
    crash_multiplier = round(random.uniform(1.0, 5.0), 2)

    if cashout_multiplier <= crash_multiplier:
        winnings = bet_amount * cashout_multiplier
        current_user.balance += winnings
        result = 'win'
    else:
        winnings = 0
        result = 'crash'

    db.session.commit()
    return jsonify({
        'result': result,
        'crash_multiplier': crash_multiplier,
        'winnings': winnings,
        'new_balance': current_user.balance
    })

@app.route('/api/complete-job', methods=['POST'])
@login_required
def complete_job():
    data = request.get_json() or {}
    job_id = data.get('job_id')
    job = Job.query.get(job_id)

    if job:
        current_user.balance += job.payout
        db.session.commit()
        return jsonify({'success': True, 'payout': job.payout, 'new_balance': current_user.balance})
    return jsonify({'success': False, 'message': 'Task not found.'}), 404

# Auto-initialize database tables and default freelance jobs
with app.app_context():
    db.create_all()
    if Job.query.count() == 0:
        sample_jobs = [
            Job(title="Website Bug Fix", description="Debug CSS layout issue on responsive nav bar.", payout=15.00),
            Job(title="Logo Design", description="Create a modern vector icon for an e-commerce brand.", payout=25.00),
            Job(title="Content Writing", description="Write a 500-word blog post on tech trends.", payout=10.00)
        ]
        db.session.bulk_save_objects(sample_jobs)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
