
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from mede_control import meds_bp
import os

app = Flask(__name__)

#app.register_blueprint(meds_bp, url_prefix="/meds")
app.secret_key = 'sua_chave_secreta_aqui'  # obrigatório para sessões

DB_NAME_COTATION = 'users.db'

# Context processor para usar {{ brand }} e {{ now().year }}
@app.context_processor
def inject_brand():
    from datetime import datetime
    return {"brand": "AMO Solutions", "now": datetime.now}


### ----------------------------------  GENERAL -------------------------------------------
# Home -------------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html', page_title="Home")

@app.route('/enginee')
def enginee():
    return render_template('Source/engineering.html', page_title="Engineering Solutions")

@app.route('/cotations')
def cotations():
    if not session.get('user_id'):
        flash("Faça login para acessar Cotations.")
        return redirect(url_for('login'))
    return render_template('cotations.html', page_title="Cotations")

@app.route('/others')
def others():
    return render_template('Source/others.html', page_title="Others Applications")

@app.route('/project')
def project():
    return render_template('Source/projects.html', page_title="Projects")

@app.route('/about')
def about():
    return render_template('Source/about.html', page_title="About US")


# Página de login ------------------------------------------------------------------------------
@app.route('/login_cotation', methods=['GET', 'POST'])
def login_cotation():
    if request.method == 'POST':
        identifier = request.form['identifier']  # pode ser email ou username
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? OR username=?", (identifier, identifier))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            flash(f"Bem-vindo(a), {user['full_name']}!")
            return redirect(url_for('cotations'))
        else:
            flash("Usuário ou senha incorretos.")
            return redirect(url_for('login'))

    return render_template('Source/login-cotation.html', page_title="Login")


# Página de cadastro --------------------------------------------------------------------
@app.route('/register_cotation', methods=['GET', 'POST'])
def register_cotation():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (full_name, username, email, password) VALUES (?, ?, ?, ?)",
                (full_name, username, email, password)
            )
            conn.commit()
            conn.close()
            flash("Cadastro realizado com sucesso! Faça login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email ou usuário já cadastrado.")
            return redirect(url_for('register_cotation'))

    return render_template('Source/register-cotation.html', page_title="Cadastro")


# Logout ---------------------------------------------------------------------------------------------
@app.route('/logout_cotation')
def logout_cotation():
    session.clear()
    flash("Você foi desconectado.")
    return redirect(url_for('index'))
#--
#--
#--
### ---------------------------------- Engineering Solution -------------------------------------------

@app.route('/voltage_drop')
def voltage_drop():
    return render_template('Enginee/voltage.html', page_title="Voltage Drop")


@app.route('/isa')
def isa():
    return render_template('Enginee/isa-51.html', page_title="ISA 5.1")


@app.route('/excel_upload', methods=['GET', 'POST'])
def excel_upload():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            flash("Nenhum arquivo enviado.")
            return redirect(url_for('excel_upload'))

        df = pd.read_excel(file)  # lê planilha
        data = df.to_dict(orient="records")  # lista de dicionários [{col1: v1, col2: v2, ...}, ...]

        return render_template("Enginee/excel_table.html", data=data, page_title="Tabela Excel")

    # se for GET, mostra a tela de upload
    return render_template("Enginee/read_table_browser.html", page_title="Upload Excel")


@app.route('/eletro_dim')
def eletro_dim():
    return render_template('Enginee/eletro-dimension.html', page_title="Eletro Dimension")


@app.route('/cabletray_dim')
def cabletray_dim():
    return render_template('Enginee/cabletray-dimension.html', page_title="Cable Tray Dimension")




### ------------------------------------ Med ----------------------------------------------

DB_NAME_MED = os.path.join(os.path.dirname(__file__), 'meds.db')

def get_db_connection():
    conn = sqlite3.connect(DB_NAME_MED)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register_med', methods=['GET', 'POST'])
def register_med():
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
            return redirect(url_for('login_med'))
        conn.close()
    return render_template('meds/register-med.html')

@app.route('/login_med', methods=['GET', 'POST'])
def login_med():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['meds_user_id'] = user['id']
            session['meds_username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Login inválido', 'danger')
    return render_template('meds/login-med.html')

@app.route('/logout_med')
def logout_med():
    session.pop('meds_user_id', None)
    session.pop('meds_username', None)
    return redirect(url_for('login_med'))

@app.route('/dashboard')
def dashboard():
    if 'meds_user_id' not in session:
        return redirect(url_for('login_med'))
    conn = get_db_connection()
    meds = conn.execute('SELECT * FROM medications WHERE user_id = ?', (session['meds_user_id'],)).fetchall()
    conn.close()
    return render_template('meds/dashboard.html', meds=meds)

@app.route('/add_med', methods=['GET', 'POST'])
def add_med():
    if 'meds_user_id' not in session:
        return redirect(url_for('login_med'))
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
        return redirect(url_for('dashboard'))
    return render_template('meds/add_med.html')

@app.route('/take_med/<int:med_id>')
def take_med(med_id):
    if 'meds_user_id' not in session:
        return redirect(url_for('login_med'))
    conn = get_db_connection()
    med = conn.execute('SELECT * FROM medications WHERE id = ? AND user_id = ?', (med_id, session['meds_user_id'])).fetchone()
    if med:
        conn.execute('INSERT INTO timeline (med_id, user_id, taken_at) VALUES (?, ?, datetime("now"))',
                     (med_id, session['meds_user_id']))
        new_total = med['total_pills'] - med['pills_per_dose']
        conn.execute('UPDATE medications SET total_pills = ? WHERE id = ?', (new_total, med_id))
        conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/timeline/<int:med_id>')
def timeline(med_id):
    if 'meds_user_id' not in session:
        return redirect(url_for('login_med'))
    conn = get_db_connection()
    med = conn.execute('SELECT * FROM medications WHERE id = ? AND user_id = ?', (med_id, session['meds_user_id'])).fetchone()
    logs = conn.execute('SELECT * FROM timeline WHERE med_id = ? AND user_id = ? ORDER BY taken_at DESC',
                        (med_id, session['meds_user_id'])).fetchall()
    conn.close()
    return render_template('meds/timeline.html', med=med, logs=logs)














#Inicia Site
#---------------------------------------------------
app.config['TEMPLATES_AUTO_RELOAD'] = True
#app.register_blueprint(meds_bp)
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)

