from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = os.path.join(os.path.dirname(__file__), 'meds.db')
meds_bp = Blueprint('meds', __name__, url_prefix='/meds')

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@meds_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        existing = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            flash('Usuário já existe!', 'danger')
        else:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, generate_password_hash(password)))
            conn.commit()
            flash('Cadastro realizado, faça login.', 'success')
            return redirect(url_for('meds.login'))
        conn.close()
    return render_template('meds/register.html')

@meds_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['meds_user_id'] = user['id']
            session['meds_username'] = user['username']
            return redirect(url_for('meds.dashboard'))
        else:
            flash('Login inválido', 'danger')
    return render_template('meds/login.html')

@meds_bp.route('/logout')
def logout():
    session.pop('meds_user_id', None)
    session.pop('meds_username', None)
    return redirect(url_for('meds.login'))

@meds_bp.route('/dashboard')
def dashboard():
    if 'meds_user_id' not in session:
        return redirect(url_for('meds.login'))
    conn = get_db_connection()
    meds = conn.execute('SELECT * FROM medications WHERE user_id = ?', (session['meds_user_id'],)).fetchall()
    conn.close()
    return render_template('meds/dashboard.html', meds=meds)

@meds_bp.route('/add_med', methods=['GET', 'POST'])
def add_med():
    if 'meds_user_id' not in session:
        return redirect(url_for('meds.login'))
    if request.method == 'POST':
        name = request.form['name']
        total_pills = int(request.form['total_pills'])
        pills_per_dose = int(request.form['pills_per_dose'])
        times_per_day = int(request.form['times_per_day'])
        conn = get_db_connection()
        conn.execute('INSERT INTO medications (user_id, name, total_pills, pills_per_dose, times_per_day) VALUES (?, ?, ?, ?, ?)',
                     (session['meds_user_id'], name, total_pills, pills_per_dose, times_per_day))
        conn.commit()
        conn.close()
        return redirect(url_for('meds.dashboard'))
    return render_template('meds/add_med.html')

@meds_bp.route('/take_med/<int:med_id>')
def take_med(med_id):
    if 'meds_user_id' not in session:
        return redirect(url_for('meds.login'))
    conn = get_db_connection()
    med = conn.execute('SELECT * FROM medications WHERE id = ? AND user_id = ?', (med_id, session['meds_user_id'])).fetchone()
    if med:
        conn.execute('INSERT INTO timeline (med_id, user_id, taken_at) VALUES (?, ?, datetime("now"))',
                     (med_id, session['meds_user_id']))
        new_total = med['total_pills'] - med['pills_per_dose']
        conn.execute('UPDATE medications SET total_pills = ? WHERE id = ?', (new_total, med_id))
        conn.commit()
    conn.close()
    return redirect(url_for('meds.dashboard'))

@meds_bp.route('/timeline/<int:med_id>')
def timeline(med_id):
    if 'meds_user_id' not in session:
        return redirect(url_for('meds.login'))
    conn = get_db_connection()
    med = conn.execute('SELECT * FROM medications WHERE id = ? AND user_id = ?', (med_id, session['meds_user_id'])).fetchone()
    logs = conn.execute('SELECT * FROM timeline WHERE med_id = ? AND user_id = ? ORDER BY taken_at DESC',
                        (med_id, session['meds_user_id'])).fetchall()
    conn.close()
    return render_template('meds/timeline.html', med=med, logs=logs)
