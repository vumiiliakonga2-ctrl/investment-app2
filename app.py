from flask import Flask, render_template, request, redirect
import sqlite3
import os
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

def send_telegram_alert(message):
    if BOT_TOKEN and ADMIN_CHAT_ID:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID, "text": message})

def init_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        wallet TEXT
    )''')
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        wallet = request.form["wallet"]

        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, wallet) VALUES (?, ?, ?)", (name, email, wallet))
        conn.commit()
        conn.close()

        send_telegram_alert(f"📥 New registration:\n👤 {name}\n📧 {email}\n💼 {wallet}")
        return render_template("thankyou.html", name=name)
    
    return render_template("register.html")

@app.route("/dashboard/<email>")
def dashboard(email):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cur.fetchone()
    conn.close()

    if not user:
        return "User not found."
    return render_template("dashboard.html", user=user)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
