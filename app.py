from flask import Flask, render_template, request, redirect, url_for, session
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
