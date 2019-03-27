from flask import Flask, redirect, session, url_for, request, render_template, send_file, make_response
from spellchecker import SpellChecker
from werkzeug.security import generate_password_hash,  check_password_hash
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.validators import ValidationError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

#from passlib.hash import sha256_crypt
from flask_login import current_user, LoginManager,  login_user, login_required, logout_user, UserMixin
import os
import atexit


counter = 0
spell = SpellChecker()
app = Flask(__name__)
app.secret_key = os.urandom(24)
engine = create_engine("mysql://root:S@hil3540@localhost/users4")
if not database_exists(engine.url):
    create_database(engine.url)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:S@hil3540@localhost/users4'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(50),unique=True, nullable=False)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    passwd = db.Column(db.String(100))

class RegisterForm(Form):
    FirstName = StringField('FirstName', [validators.InputRequired(), validators.Length(min=1,max=30)])
    LastName = StringField('LastName', [validators.InputRequired(), validators.Length(min=1, max=30)])
    username = StringField('username', [validators.InputRequired(), validators.Length(min=5, max=10)])
    Password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('ConfirmPassword', message='Passwords do not match')
    ])
    ConfirmPassword = PasswordField('ConfirmPassword')
    '''
    def validate_username(self, username):
        user = Users.query.filter_by(uname=uname.data).first()
        if user:
            print("here")
            raise ValidationError('That username is taken. Please choose a different one')
'''
class LoginForm(Form):
    username = StringField('username', [validators.InputRequired(), validators.Length(min=5, max=10)])
    password = StringField('password', [validators.InputRequired(), validators.Length(min=5, max=10)])

db.create_all()


@login_manager.user_loader
def user_loader(uname):
    return Users.query.get(uname)

@app.route('/')
@app.route('/index')
def hello_world():
    print ('test')
    return render_template('index.html')

@app.route('/return-file/')
def return_file():
    return send_file('output.txt', attachment_filename='output.txt', cache_timeout=-1)

@app.route('/processing',methods=['POST','GET'])
def processing():
    if request.method == 'POST':
        message = request.form['message']
        misspelled = spell.unknown(str(message).split(' '))
        result = ' '
        for word in misspelled:
            # Get the one `most likely` answer
            result = result + spell.correction(word)
            result = result + " "
        return render_template('result.html',message=result)
    else:
        message = request.args.get('message')
        misspelled = spell.unknown(str(message).split(' '))
        result = ' '
        for word in misspelled:
            # Get the one `most likely` answer
            result = result + spell.correction(word)
            result = result + " "
        return render_template('result.html',message=result)

def check_file(f):
    fi = open(f.filename, "r")
    final = open("output.txt","w")
    misspelled = spell.unknown(str(fi.read()).split(' '))
    result = ' '
    for word in misspelled:
        # Get the one `most likely` answer
        result = result + spell.correction(word)
        result = result + " "
        print(result)
    final.write(result)
    final.close()
    fi.close()
    os.remove(f.filename)

@app.route('/uploader',methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        #print(f.filename)
        check_file(f)
        return render_template('result.html',message="File uploaded Successsfuly")

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    print("in login")
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = Users.query.filter_by(uname = request.form['username']).first()
        if user:
            print(user.passwd)
            if check_password_hash(user.passwd, request.form['password']):
                login_user(user, remember=True)
                user.authenticated = True
                return redirect(url_for('dashboard'))
    return render_template('Login.html', form=form)
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for("login"))
@app.route('/Register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm(request.form)
    global counter
    if request.method == 'POST' and form.validate():
        #counter = counter + 1
        fname = request.form['FirstName']
        lname = request.form['LastName']
        uname = request.form['username']
        passwd = request.form['Password']
        passwd = generate_password_hash(passwd, method='sha256')
        u = Users(uname=uname, fname=fname, lname= lname, passwd=passwd )
        db.session.add(u)
        db.session.commit()

        return render_template('Register.html', message='You are registered successfully!!')
    return render_template('Register.html', form=form, message='Registeration initiating')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

def clear():
    for tbl in reversed(meta.sorted_tables):
        engine.execute(tbl.delete())

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug = True)
    atexit.register(clear)