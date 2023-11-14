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
from sqlalchemy import func

# App setup
app = Flask(__name__)

app.config['SECRET_KEY'] = 'many random bytes'
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# setting up users database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fiszkomania.db'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = "Zaloguj się, aby wejść na stronę"
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# creating database models
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(), nullable=True)
    progress = db.relationship('Progress', back_populates='user')
    def __repr__(self):
        return '<Name %r>' % self.username

class Module(db.Model):
    module_id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(255), nullable=False, unique=True)
    module_description = db.Column(db.String(255), nullable= True)

    progress = db.relationship('Progress', back_populates='module')
    flashcards = db.relationship('Flashcards', backref='module')
    def __repr__(self):
        return self.module_name

class Flashcards(db.Model):
    flashcard_id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.String(200), nullable=False)
    back = db.Column(db.String(200), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.module_id'), nullable=False)
    def __repr__(self):
        return str(self.flashcard_id) + self.front + self.back

class Progress(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.module_id'), primary_key=True)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcards.flashcard_id'), primary_key=True)
    
    quiz = db.Column(db.Boolean, nullable=False, default=False)
    listening = db.Column(db.Boolean, nullable=False, default=False)
    speaking = db.Column(db.Boolean, nullable=False, default=False)
    writing = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('Users', back_populates='progress')
    module = db.relationship('Module', back_populates='progress')

with app.app_context():
    db.create_all()

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

@app.route('/modules')
@login_required
def modules():
    modules = db.session.query(Module.module_id, Module.module_name).all()
    return render_template('modules.html', modules=modules)

@app.route('/signup-to-course-<id>')
@login_required
def addUserToCourse(id):
    user = current_user
    module = Module.query.get(id)
    user_module_progress = Progress.query.filter_by(user=user, module=module).all()
    if user_module_progress:
        print("This user is already assigned to this module")
    else:
        flashcards = Flashcards.query.filter_by(module_id = id).all()
        for flashcard in flashcards:
            progress = Progress(user = user, module = module, flashcard_id = flashcard.flashcard_id)
            db.session.add(progress)
        db.session.commit()
        print("Records added succesfully")
    return redirect(url_for('modules'))

@app.route('/module_id=<id>')
@login_required
def modulePanel(id):
    flashcards = Flashcards.query.filter_by(module_id = id).order_by(func.random()).all()
    moduleName = Module.query.filter_by(module_id = id).first()
    flashcards_rows = [(flashcard.flashcard_id, flashcard.front, flashcard.back, flashcard.module_id) for flashcard in flashcards]
    user_already_signed = Progress.query.filter_by(user=current_user, module=Module.query.get(id)).all()
    if user_already_signed:
        hide = True
    else:
        hide = False
    return render_template('flashcards.html', table_name=moduleName, flashcards=flashcards_rows, moduleID = id, hide = hide)

@app.route('/module_id=<id>-quiz')
@login_required
def quiz(id):
    flashcards = Flashcards.query.filter_by(module_id = id).order_by(func.random()).all()
    flashcards_rows = []
    moduleName = Module.query.filter_by(module_id = id).first()
    for flashcard in flashcards:
        flashcard_row = Progress.query.filter_by(user_id = current_user.id, flashcard_id = flashcard.flashcard_id).first()
        do_i_get_it = flashcard_row.quiz
        if do_i_get_it == False:
            flashcards_rows.append((flashcard.flashcard_id, flashcard.back, flashcard.front, flashcard.module_id))
    return render_template('quiz.html', table_name=moduleName, flashcards=flashcards_rows, module_id=id)

@app.route('/set-quiz-true-<flashcard_id>')
@login_required
def setQuizTrue(flashcard_id):
    progress = Progress.query.filter_by(user_id=current_user.id, flashcard_id=flashcard_id).first()
    if progress:
        progress.quiz = True
        db.session.commit()
    return "bla bla bla"

@app.route('/set-quiz-false-<module_id>')
@login_required
def setQuizFalse(module_id):
    progress = Progress.query.filter_by(user_id=current_user.id, module_id=module_id).all()
    for row in progress:
        row.quiz = False
        db.session.commit()
    return redirect(url_for('quiz', id=module_id))


@app.route('/module_id=<id>-writing')
@login_required
def writing(id):
    flashcards = Flashcards.query.filter_by(module_id = id).order_by(func.random()).all()
    flashcards_rows = []
    moduleName = Module.query.filter_by(module_id = id).first()
    for flashcard in flashcards:
        flashcard_row = Progress.query.filter_by(user_id = current_user.id, flashcard_id = flashcard.flashcard_id).first()
        do_i_get_it = flashcard_row.writing
        if do_i_get_it == False:
            flashcards_rows.append((flashcard.flashcard_id, flashcard.back, flashcard.front, flashcard.module_id))
    return render_template('writing.html', table_name=moduleName, flashcards=flashcards_rows, module_id=id)

@app.route('/set-writing-true-<flashcard_id>')
@login_required
def setWritingTrue(flashcard_id):
    user = current_user
    progress = Progress.query.filter_by(user_id=current_user.id, flashcard_id=flashcard_id).first()
    if progress:
        progress.writing = True
        db.session.commit()
    return "bla bla bla"

@app.route('/set-writing-false-<module_id>')
@login_required
def setWritingFalse(module_id):
    progress = Progress.query.filter_by(user_id=current_user.id, module_id=module_id).all()
    for row in progress:
        row.writing = False
        db.session.commit()
    return redirect(url_for('writing', id=module_id))

@app.route('/module_id=<id>-listening')
@login_required
def listening(id):
    flashcards = Flashcards.query.filter_by(module_id = id).order_by(func.random()).all()
    flashcards_rows = []
    moduleName = Module.query.filter_by(module_id = id).first()
    for flashcard in flashcards:
        flashcard_row = Progress.query.filter_by(user_id = current_user.id, flashcard_id = flashcard.flashcard_id).first()
        do_i_get_it = flashcard_row.listening
        if do_i_get_it == False:
            flashcards_rows.append((flashcard.flashcard_id, flashcard.back, flashcard.front, flashcard.module_id))
    return render_template('listening.html', table_name=moduleName, flashcards=flashcards_rows, module_id=id)

@app.route('/set-listening-true-<flashcard_id>')
@login_required
def setListeningTrue(flashcard_id):
    user = current_user
    progress = Progress.query.filter_by(user_id=current_user.id, flashcard_id=flashcard_id).first()
    if progress:
        progress.listening = True
        db.session.commit()
    return "bla bla bla"

@app.route('/set-listening-false-<module_id>')
@login_required
def setListeningFalse(module_id):
    progress = Progress.query.filter_by(user_id=current_user.id, module_id=module_id).all()
    for row in progress:
        row.listening = False
        db.session.commit()
    return redirect(url_for('listening', id=module_id))

@app.route('/module_id=<id>-speaking')
@login_required
def speaking(id):
    flashcards = Flashcards.query.filter_by(module_id = id).order_by(func.random()).all()
    flashcards_rows = []
    moduleName = Module.query.filter_by(module_id = id).first()
    for flashcard in flashcards:
        flashcard_row = Progress.query.filter_by(user_id = current_user.id, flashcard_id = flashcard.flashcard_id).first()
        do_i_get_it = flashcard_row.speaking
        if do_i_get_it == False:
            flashcards_rows.append((flashcard.flashcard_id, flashcard.back, flashcard.front, flashcard.module_id))
    return render_template('speaking.html', table_name=moduleName, flashcards=flashcards_rows, module_id=id)

@app.route('/set-speaking-true-<flashcard_id>')
@login_required
def setSpeakingTrue(flashcard_id):
    user = current_user
    progress = Progress.query.filter_by(user_id=current_user.id, flashcard_id=flashcard_id).first()
    if progress:
        progress.speaking = True
        db.session.commit()
    return "bla bla bla"

@app.route('/set-speaking-false-<module_id>')
@login_required
def setSpeakingFalse(module_id):
    progress = Progress.query.filter_by(user_id=current_user.id, module_id=module_id).all()
    for row in progress:
        row.speaking = False
        db.session.commit()
    return redirect(url_for('speaking', id=module_id))

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