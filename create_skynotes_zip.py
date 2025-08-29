import os
import json
import zipfile

project_name = "SkyNotes"
files = {
    "app.py": """from flask import Flask, render_template, request, redirect, url_for, session
import json, os

app = Flask(__name__)
app.secret_key = "sky_secret_key"
DATA_PATH = "data"
os.makedirs(DATA_PATH, exist_ok=True)

users_file = os.path.join(DATA_PATH, "users.json")
notes_file = os.path.join(DATA_PATH, "notes.json")
if not os.path.exists(users_file):
    with open(users_file, "w") as f:
        json.dump({}, f)
if not os.path.exists(notes_file):
    with open(notes_file, "w") as f:
        json.dump({}, f)

def load_users():
    with open(users_file,"r") as f:
        return json.load(f)
def save_users(users):
    with open(users_file,"w") as f:
        json.dump(users,f,indent=4)
def load_notes():
    with open(notes_file,"r") as f:
        return json.load(f)
def save_notes(notes):
    with open(notes_file,"w") as f:
        json.dump(notes,f,indent=4)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('notes'))
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        users=load_users()
        if username in users:
            return 'Пользователь уже существует!'
        users[username]={'password':password}
        save_users(users)
        session['username']=username
        return redirect(url_for('notes'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        users=load_users()
        if username in users and users[username]['password']==password:
            session['username']=username
            return redirect(url_for('notes'))
        return 'Неверные данные!'
    return render_template('login.html')

@app.route('/guest')
def guest():
    session['username']='Guest'
    return redirect(url_for('notes'))

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route('/notes', methods=['GET','POST'])
def notes():
    if 'username' not in session:
        return redirect(url_for('login'))
    username=session['username']
    notes=load_notes()
    if username not in notes:
        notes[username]=[]
    if request.method=='POST':
        action=request.form.get('action')
        content=request.form.get('content')
        index=request.form.get('index')
        if action=='add' and content:
            notes[username].append(content)
        elif action=='delete' and index:
            notes[username].pop(int(index))
        elif action=='edit' and index and content:
            notes[username][int(index)]=content
        save_notes(notes)
        return redirect(url_for('notes'))
    return render_template('notes.html', notes=notes[username], username=username)

@app.route('/delete_account')
def delete_account():
    if 'username' in session and session['username']!='Guest':
        username=session['username']
        users=load_users()
        notes=load_notes()
        users.pop(username,None)
        notes.pop(username,None)
        save_users(users)
        save_notes(notes)
        session.pop('username',None)
    return redirect(url_for('index'))

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
""",
    "templates/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SkyNotes</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-r from-blue-400 to-indigo-600 flex items-center justify-center h-screen">
<div class="bg-white p-12 rounded-3xl shadow-2xl text-center w-96">
    <h1 class="text-4xl font-bold mb-8 text-indigo-700">SkyNotes</h1>
    <a href="/login" class="block bg-blue-500 text-white py-3 px-6 rounded-xl mb-4 hover:bg-blue-600 transition">Вход</a>
    <a href="/register" class="block bg-green-500 text-white py-3 px-6 rounded-xl mb-4 hover:bg-green-600 transition">Регистрация</a>
    <a href="/guest" class="block bg-gray-500 text-white py-3 px-6 rounded-xl hover:bg-gray-600 transition">Вход как гость</a>
</div>
</body>
</html>
""",
    "templates/register.html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Регистрация — SkyNotes</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-r from-purple-400 to-pink-500 flex items-center justify-center h-screen">
<div class="bg-white p-10 rounded-3xl shadow-xl w-96">
<h1 class="text-3xl font-bold mb-6 text-purple-700">Регистрация</h1>
<form method="POST" class="space-y-4">
    <input type="text" name="username" placeholder="Имя пользователя" class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-purple-300">
    <input type="password" name="password" placeholder="Пароль" class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-purple-300">
    <button class="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition">Зарегистрироваться</button>
</form>
<a href="/" class="block mt-4 text-purple-800 text-center hover:underline">Назад</a>
</div>
</body>
</html>
""",
    "templates/login.html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Вход — SkyNotes</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-r from-blue-400 to-indigo-500 flex items-center justify-center h-screen">
<div class="bg-white p-10 rounded-3xl shadow-xl w-96">
<h1 class="text-3xl font-bold mb-6 text-blue-700">Вход</h1>
<form method="POST" class="space-y-4">
    <input type="text" name="username" placeholder="Имя пользователя" class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-300">
    <input type="password" name="password" placeholder="Пароль" class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-300">
    <button class="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition">Войти</button>
</form>
<a href="/" class="block mt-4 text-blue-800 text-center hover:underline">Назад</a>
</div>
</body>
</html>
""",
    "templates/notes.html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SkyNotes — Мои заметки</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-r from-blue-300 to-indigo-400 p-10 min-h-screen">
<div class="max-w-3xl mx-auto bg-white p-8 rounded-3xl shadow-xl">
<h1 class="text-3xl font-bold mb-6 text-indigo-700">Привет, {{ username }}!</h1>
<form method="POST" class="mb-6 flex space-x-2">
    <input type="hidden" name="action" value="add">
    <input type="text" name="content" placeholder="Новая заметка" class="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-indigo-300">
    <button class="bg-indigo-600 text-white px-6 rounded-lg hover:bg-indigo-700 transition">Добавить</button>
</form>
<ul class="space-y-3">
{% for note in notes %}
<li class="flex justify-between items-center p-3 border rounded-lg bg-indigo-50">
    <span class="flex-1">{{ note }}</span>
    <form method="POST" class="flex space-x-2">
        <input type="hidden" name="index" value="{{ loop.index0 }}">
        <input type="text" name="content" placeholder="Редактировать" class="p-2 border rounded-lg">
        <button name="action" value="edit" class="bg-yellow-400 px-3 rounded hover:bg-yellow-500 transition">Изм.</button>
        <button name="action" value="delete" class="bg-red-500 text-white px-3 rounded hover:bg-red-600 transition">Удалить</button>
    </form>
</li>
{% endfor %}
</ul>
<div class="mt-6 flex space-x-4">
<a href="/logout" class="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 transition">Выйти</a>
{% if username != "Guest" %}
<a href="/delete_account" class="bg-red-700 text-white py-2 px-4 rounded hover:bg-red-800 transition">Удалить аккаунт</a>
{% endif %}
</div>
</div>
</body>
</html>
""",
    "data/users.json": "{}",
    "data/notes.json": "{}",
}

# Создаём структуру и файлы
for path, content in files.items():
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Создаём zip
zip_name = "SkyNotes.zip"
with zipfile.ZipFile(zip_name, "w") as zipf:
    for path in files:
        zipf.write(path)

print(f"Проект SkyNotes создан и упакован в {zip_name}")
