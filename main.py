### NOTATKI:

## Kolejny krok to dodać zabezpieczenie wymagania zalogowania zeby przejsc do strony home i wyswietlac uzytkownika
## Jest do tego biblioteka LoginManager ale wymaga to ode mnie operacji na obiekcie User i haszowaniu hasła
## Dlatego muszę przerobić kod tak aby działał na obiekcie User to jego dodawał do bazy oraz posiadał haszowanie hasła
## Potem kolejne kroki aby użyć LoginManagera 

import sqlite3
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# App setup
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'many random bytes'
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = "Zaloguj się, aby wejść na stronę"
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(), nullable=True)
    def __repr__(self):
        return '<Name %r>' % self.username

with app.app_context():
    db.create_all()

# Connections to databases
connection_flashcard = sqlite3.connect("fiszki.db");
cursor_flashcard = connection_flashcard.cursor();
cursor_flashcard.execute("SELECT * FROM Module_2");
rows = cursor_flashcard.fetchall();
first = rows[0];


# Routes
@app.route('/')
def index():
    return render_template('index.html');

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
    
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("Błędne hasło. Spróbuj ponownie")
                return redirect(url_for('login'))
        else:
            flash("Użytkownik o takiej nazwie nie istnieje")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()

        if user:
            flash("Użytkownik o takiej nazwie już istnieje. Spróbuj ponownie")
            return redirect(url_for('signup'))
        
        new_user = Users(username=username, password=generate_password_hash(password, method='sha256'))

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/home')
@login_required
def home():
    pol_def = str(rows[0][1])
    hiszp_def = str(rows[0][2])
    return render_template('home.html', pol_def=pol_def, hiszp_def=hiszp_def)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    image_files = [f for f in os.listdir('static/images/default') if f.endswith(('jpg', 'png', 'gif'))]
    return render_template('dashboard.html', image_files=image_files)

@app.route('/add-avatar', methods=['GET', 'POST'])
@login_required
def add_avatar():
    image_files = [f for f in os.listdir('static/images/default') if f.endswith(('jpg', 'png', 'gif'))]
    if request.method == 'POST':
        if request.files['profile_picture']:
            profile_picture = request.files['profile_picture']
            user_update = Users.query.get_or_404(current_user.id)
            user_update.profile_picture = profile_picture
            picture_file_name = secure_filename(user_update.profile_picture.filename)
            picture_unique_name = str(uuid.uuid1()) + '_' + picture_file_name
            user_update.profile_picture = picture_unique_name
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_unique_name))
        elif request.form.get('image_option'):
            profile_picture = 'default/'+request.form['image_option']
            user_update = Users.query.get_or_404(current_user.id)
            user_update.profile_picture = profile_picture  
        db.session.commit()
    return render_template('dashboard.html', image_files=image_files)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def changePassword():
    if request.method == 'POST':

        user_update = Users.query.get_or_404(current_user.id)
        #old_password = generate_password_hash(request.form['old_password'], method='sha256')
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        new_password_repeat = request.form['new_password_repeat']


        if check_password_hash(current_user.password, old_password):
            if new_password == new_password_repeat:
                user_update.password = generate_password_hash(new_password)
                db.session.commit()
                flash("Hasło zostało zmienione")
                return redirect(url_for('dashboard'))
            else:
                flash("Hasło i powtórzone hasło są różne")
                return redirect(url_for('changePassword'))
        else:
            flash("Błędne hasło. Spróbuj ponownie.")
            return redirect(url_for('changePassword'))
        
    return render_template('change_password.html')

if __name__ == "__main__":
    app.run(debug=True)