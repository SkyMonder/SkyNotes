import os
import json
import time
import threading
import subprocess
from flask import Flask, render_template, request, redirect, session, url_for, flash

# === Настройки Flask ===
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

# === Пути к базам ===
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

# === Утилиты для работы с базами ===
def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === Маршруты ===

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("notes"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    users = load_json(USERS_FILE)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if any(u["username"] == username for u in users):
            flash("Такой пользователь уже существует.")
            return redirect(url_for("register"))
        users.append({"username": username, "password": password})
        save_json(USERS_FILE, users)
        flash("Регистрация успешна, войдите в систему.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    users = load_json(USERS_FILE)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        for user in users:
            if user["username"] == username and user["password"] == password:
                session["username"] = username
                return redirect(url_for("notes"))
        flash("Неверный логин или пароль.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/notes", methods=["GET", "POST"])
def notes():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    notes = load_json(NOTES_FILE)

    if request.method == "POST":
        text = request.form["note"]
        if text.strip():
            notes.append({"username": username, "note": text})
            save_json(NOTES_FILE, notes)
    user_notes = [n for n in notes if n["username"] == username]
    return render_template("notes.html", notes=user_notes, username=username)

# === 🪄 Автобэкап данных на GitHub ===

BACKUP_INTERVAL = 24 * 60 * 60  # 24 часа
GIT_EMAIL = "render-bot@example.com"
GIT_NAME = "Render Auto Backup"
REPO_URL = os.getenv("GIT_REPO_URL")  # переменная окружения в Render

def restore_data_from_git():
    """Восстановление базы при старте"""
    if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
        print("🗂 Восстанавливаем базу данных из GitHub...")
        if os.path.exists(".git"):
            subprocess.run(["git", "pull"], check=False)
        else:
            subprocess.run(["git", "clone", REPO_URL, "."], check=False)
        print("✅ Данные восстановлены из репозитория.")

def auto_backup():
    """Ежедневный бэкап JSON в GitHub"""
    while True:
        try:
            subprocess.run(["git", "config", "user.email", GIT_EMAIL])
            subprocess.run(["git", "config", "user.name", GIT_NAME])
            subprocess.run(["git", "add", DATA_DIR], check=False)
            subprocess.run(["git", "commit", "-m", "Daily auto-backup of data"], check=False)
            subprocess.run(["git", "push", "origin", "main"], check=False)
            print("💾 Ежедневный бэкап успешно отправлен на GitHub.")
        except Exception as e:
            print("⚠️ Ошибка при автосохранении:", e)
        time.sleep(BACKUP_INTERVAL)

# === Запуск при старте ===
if __name__ == "__main__":
    restore_data_from_git()
    threading.Thread(target=auto_backup, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
