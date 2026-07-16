import os
import sqlite3
import random
import requests
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, session, jsonify

app = Flask(__name__)
app.secret_key = "abc_abbaa_carraa_secret_key_2026"
DATABASE = 'abc_carraa.db'

# 🌐 CHAPA & TELEGRAM CONFIGURATION
CHAPA_SECRET_KEY = os.environ.get("CHAPA_SECRET_KEY", "CHASECK_TEST-LoLEWjO25hQf4wsNILomYDrMdiwLdeOd")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "7410298642:AAEL74RjI6-9bXvXj9Bv4g9tU7FvXj9Bv4g")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1167731453")

# 🌍 MULTILINGUAL TRANSLATION DICTIONARY (AFAANOTA SADI)
LANG_DICT = {
    'om': {
        'welcome': 'Baga Gammadde gara ABC', 'slogan': 'Abbaa Carraa', 'login': 'Seeni', 'register': 'Galmaa\'i',
        'fullname': 'Maqaa Guutuu', 'phone': 'Lakkoofsa Bilbilaa', 'password': 'Password', 'logout': 'Bahi',
        'daily': 'Carraa Guyyaa', 'weekly': 'Carraa Torbanii', 'monthly': 'Carraa Ji\'aa', 'event': 'Carraa Addaa (Event)',
        'participants': 'Lakkoofsa Hirmaattotaa', 'spin': '🎰 CARRAA BAASI', 'winners': 'Seenaa Injifattootaa', 'winner': 'Maqaa Injifataa'
    },
    'am': {
        'welcome': 'እንኳን ወደ ABC በደህና መጡ', 'slogan': 'አባ ጨራ', 'login': 'ግባ', 'register': 'ተመዝገብ',
        'fullname': 'ሙሉ ስም', 'phone': 'የስልክ ቁጥር', 'password': 'የይለፍ ቃል', 'logout': 'ውጣ',
        'daily': 'የቀን ዕድል', 'weekly': 'የሳምንት ዕድል', 'monthly': 'የወር ዕድል', 'event': 'ልዩ ዕድል (ኢቨንት)',
        'participants': 'የተሳታፊዎች ብዛት', 'spin': '🎰 ዕድል አውጣ', 'winners': 'የአሸናፊዎች ታሪክ', 'winner': 'የአሸናፊው ስም'
    },
    'en': {
        'welcome': 'Welcome to ABC', 'slogan': 'Lucky Draw', 'login': 'Login', 'register': 'Register',
        'fullname': 'Full Name', 'phone': 'Phone Number', 'password': 'Password', 'logout': 'Logout',
        'daily': 'Daily Draw', 'weekly': 'Weekly Draw', 'monthly': 'Monthly Draw', 'event': 'Special Event Draw',
        'participants': 'Total Participants', 'spin': '🎰 SPIN WHEEL', 'winners': 'Winner History', 'winner': 'Winner Name'
    }
}

def send_telegram_message(message):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try: requests.post(url, json=payload, timeout=10)
    except Exception as e: print("Telegram error:", e)

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'User',
                status TEXT DEFAULT 'Active'
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL,
                draw_type TEXT NOT NULL,
                tx_id TEXT NOT NULL,
                status TEXT DEFAULT 'Approved',
                timestamp TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS winners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                phone TEXT NOT NULL,
                draw_type TEXT NOT NULL,
                prize TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_om TEXT NOT NULL,
                message_am TEXT NOT NULL,
                message_en TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        try: conn.execute("INSERT INTO users (fullname, phone, password, role) VALUES (?, ?, ?, ?)", ('Admin ABC', '0922822568', 'admin123', 'Admin'))
        except sqlite3.IntegrityError: pass
        conn.commit()

@app.route('/')
def home():
    lang = request.args.get('lang', 'om')
    session['lang'] = lang
    return render_template('index.html', t=LANG_DICT[lang], current_lang=lang)

@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = session.get('lang', 'om')
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        password = request.form['password']
        try:
            with get_db() as conn:
                conn.execute("INSERT INTO users (fullname, phone, password) VALUES (?, ?, ?)", (fullname, phone, password))
                conn.commit()
            send_telegram_message(f"🎫 ABC: HIRMAATAA HAARAA!\nMaqaa: {fullname}\nBilbila: {phone}")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError: return "<h1>Lakk. bilbilaa kun kanaan dura galma'eera!</h1>"
    return render_template('register.html', t=LANG_DICT[lang])

@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = session.get('lang', 'om')
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE phone = ? AND password = ?", (phone, password)).fetchone()
        conn.close()
        if user:
            session['user_phone'] = user['phone']
            session['user_name'] = user['fullname']
            session['role'] = user['role']
            if user['role'] == 'Admin': return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard_view'))
        return "<h1>User Number/Password Incorrect!</h1>"
    return render_template('login.html', t=LANG_DICT[lang])

@app.route('/dashboard')
def dashboard_view():
    if 'user_phone' not in session: return redirect(url_for('login'))
    lang = session.get('lang', 'om')
    conn = get_db()
    
    # Herrega tikitii hinda gareen addaan baasuu (Tiered Pools Display)
    counts = {}
    types = ['Daily', 'Weekly', 'Monthly', 'Event']
    for t in types:
        row = conn.execute("SELECT COUNT(*) as cnt FROM tickets WHERE draw_type = ? AND status = 'Approved'", (t,)).fetchone()
        counts[t] = row['cnt']

    winners = conn.execute("SELECT * FROM winners ORDER BY id DESC").fetchall()
    notifs = conn.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall()
    conn.close()
    
    return render_template('dashboard.html', t=LANG_DICT[lang], counts=counts, winners=winners, notifications=notifs, lang=lang)

# 🚀 BUY TICKET / ENTER DRAW (CHAPA AUTO INTEGRATION)
@app.route('/draw/enter/<draw_type>', methods=['POST'])
def enter_draw(draw_type):
    if 'user_phone' not in session: return redirect(url_for('login'))
    amount = "10" # Gatii tikiti yaalii (Customizable by admin)
    tx_id = f"abc-{session['user_phone']}-{int(datetime.now().timestamp())}"
    
    url = "https://chapa.co"
    headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}", "Content-Type": "application/json"}
    payload = {
        "amount": amount, "currency": "ETB", "phone_number": session['user_phone'],
        "first_name": session['user_name'], "last_name": "ABC", "tx_ref": tx_id,
        "callback_url": f"https://onrender.com{tx_id}/{draw_type}",
        "return_url": "https://onrender.com"
    }
    try:
        response = requests.post(url, json=payload, headers=headers).json()
        if response.get("status") == "success":
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with get_db() as conn:
                conn.execute("INSERT INTO tickets (phone, draw_type, tx_id, timestamp) VALUES (?, ?, ?, ?)", (session['user_phone'], draw_type, tx_id, now))
                conn.commit()
            return redirect(response["data"]["checkout_url"])
    except Exception as e: print(e)
    return redirect(url_for('dashboard_view'))

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'Admin': return '<h1>Unauthorized</h1>'
    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    winners = conn.execute("SELECT * FROM winners ORDER BY id DESC").fetchall()
    
    counts = {}
    for t in ['Daily', 'Weekly', 'Monthly', 'Event']:
        counts[t] = conn.execute("SELECT COUNT(*) as cnt FROM tickets WHERE draw_type = ? AND status = 'Approved'", (t,)).fetchone()['cnt']
        
    conn.close()
    return render_template('admin.html', users=users, winners=winners, counts=counts)

@app.route('/admin/spin/<draw_type>')
def admin_spin_abc(draw_type):
    if session.get('role') != 'Admin': return 'Unauthorized'
    conn = get_db()
    eligible = conn.execute("SELECT DISTINCT u.fullname, u.phone FROM users u JOIN tickets t ON u.phone = t.phone WHERE t.draw_type = ? AND t.status = 'Approved'", (draw_type,)).fetchall()
    
    if not eligible:
        conn.close()
        return "<h1>Garee kkana keessaa namni hirmaate hin jiru! <a href='/admin'>Deebi'i</a></h1>"
        
    winner = random.choice(eligible)
    now_date = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")
    prize = "Xiaomi Redmi Note 13" # Badhaasa (Dynamic customization)
    
    with get_db() as conn:
        conn.execute("INSERT INTO winners (fullname, phone, draw_type, prize, date, time) VALUES (?, ?, ?, ?, ?, ?)", (winner['fullname'], winner['phone'], draw_type, prize, now_date, now_time))
        conn.execute("UPDATE tickets SET status = 'Used' WHERE draw_type = ? AND status = 'Approved'", (draw_type,))
        conn.commit()
    conn.close()
    
    send_telegram_message(f"🎰 ABC WINNER ({draw_type})!\nMo'ataa: {winner['fullname']}\nBadhaasa: {prize}")
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
# Haaraa
