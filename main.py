import sqlite3
from flask import Flask, render_template, redirect, url_for, request

# App setup
app = Flask(__name__)

# Connections to databases
connection_flashcard = sqlite3.connect("fiszki.db");
cursor_flashcard = connection_flashcard.cursor();
cursor_flashcard.execute("SELECT * FROM Module_2");
rows = cursor_flashcard.fetchall();
first = rows[0];


# Routes
@app.route('/')
def index():
    pol_def = str(rows[0][1])
    hiszp_def = str(rows[0][2])
    return render_template('index.html', pol_def=pol_def, hiszp_def=hiszp_def);

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        connection_user = sqlite3.connect("users_dane.db");
        cursor_user = connection_user.cursor();
    
        username = request.form['username']
        password = request.form['password']

        query = "SELECT username, password FROM users WHERE username='"+username+"' AND password ='"+password+"'"
        cursor_user.execute(query)

        results = cursor_user.fetchall()

        if len(results) == 0:
           return render_template('login_false.html')
        else:
            return render_template('login_correct.html')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        connection_user = sqlite3.connect('users_dane.db')
        cursor_user = connection_user.cursor(); 

        username = request.form['username']
        password = request.form['password']
        query = "SELECT username FROM users WHERE username='"+username+"'"
        cursor_user.execute(query)

        results = cursor_user.fetchall()
        if len(results) == 0:
            add_to_base = "INSERT INTO users VALUES('"+username+"', '"+password+"')"
            cursor_user.execute(add_to_base)
            connection_user.commit()
            return render_template('registration_correct.html')
        else:
            return render_template('registration_incorrect.html')
    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True)