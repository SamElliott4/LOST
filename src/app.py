import hashlib
import psycopg2
from flask import Flask, url_for, request, render_template, redirect, session
from config import database, host, port

app = Flask(__name__)
app.secret_key = 'the secret key is "secret key"'

db = psycopg2.connect(dbname=database, host=host, port=port)
db.autocommit = True
cur = db.cursor()

# web application structure

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        if 'username' in request.form and 'password' in request.form:
            if compare_password(request.form['username'], request.form['password']): # false if username does not exist or username and password do not match
                session['username'] = get_username(request.form['username']) # Use capitalization found in database, i.e. when user was created
                return redirect(url_for('dashboard'))
            else:
                session['destination'] = url_for('login')
                session['message'] = "Invalid username or password."
                session['link_text'] = "Return to Login page."
                return redirect(url_for('direct')) 
        else:
            session['destination'] = url_for('login')
            session['message'] = "One or more fields left blank."
            session['link_text'] = "Return to Login page."
            return redirect(url_for('direct')) 
    return render_template('login.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method=='GET':
        return render_template("create_user.html")
    elif request.method=='POST':
        if 'username' in request.form and 'password' in request.form and 'password2' in request.form:
            # add_user checks for existing usernames, aborts and returns false if one is found
            if not request.form['password'] == request.form['password2']:
                session['destination'] = url_for('create_user')
                session['message'] = "Passwords do not match."
                session['link_text'] = "Return to Create User page"
            if add_user(request.form['username'], request.form['password']):
                session['destination'] = url_for('login')
                session['message'] = "Successfully created new user. Please log in."
                session['link_text'] = "Click Here"
                return redirect(url_for('direct'))    
            else:
                session['destination'] = url_for('create_user')
                session['message'] = "Username already exists."
                session['link_text'] = "Return to Create User page"
                return redirect(url_for('direct'))
        else:
            session['destination'] = url_for('create_user')
            session['message'] = "One or more fields left blank."
            session['link_text'] = "Return to Create User page."
            return redirect(url_for('direct')) 

@app.route('/dashboard', methods=['GET'])
def dashboard():
    session['destination'] = url_for('login')
    session['message'] = "Thank you for using LOST. Redirecting you to the login page"
    session['link_text'] = "Click Here"
    return render_template('dashboard.html')

@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        # Clear stored session data between logins
        del session['username']
    session['destination'] = url_for('login')
    session['message'] = "Thank you for using LOST. Returning to the login page."
    session['link_text'] = "Click Here"
    return redirect(url_for('direct'))

@app.route('/direct', methods=['GET'])
def direct():
    # Handles redirect page using information stored in session
    return render_template('redirect.html')

# supporting functions

def get_username(username):
    cur.execute("SELECT username FROM users WHERE user_id=%s;",[username.lower(),])
    user = cur.fetchone()
    return user if user is None else user[0]

def user_exists(username):
    return get_username(username) is not None

def compare_password(username, password):
    # returns true if username and password match, false otherwise
    h_pass = get_hash(password)
    cur.execute("SELECT password FROM users WHERE user_id=%s;", [username.lower(),])
    pword = cur.fetchone()
    if pword is None:
        return False
    if pword[0] == h_pass:
        return True
    return False

def add_user(username, password):
    # returns true if user is successfully created, false otherwise
    if user_exists(username):
        return False
    user_id = username.lower()
    h_pass = get_hash(password)
    try:
        cur.execute("INSERT INTO users (user_id, username, password) VALUES (%s, %s, %s);",[user_id, username, h_pass])
        db.commit()
        return True
    except:
        return False

def get_hash(string):
    return hashlib.sha256(string.encode()).hexdigest()

# run the web app when program is called
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
