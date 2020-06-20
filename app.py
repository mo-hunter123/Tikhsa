import os
from flask import Flask
from flask import request, render_template, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# from models import User_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TEST_Usrs.db'
app.config['SECRET_KEY'] = 'asfadsfsdfdsfdss'

# app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)


####################



class User_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(80), unique=True, nullable=False)
    LastName = db.Column(db.String(80), unique=True, nullable=False)
    Sexe = db.Column(db.String(18), unique=True, nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password = db.Column(db.String(18), unique=True, nullable=False)
    CIN = db.Column(db.String(18), unique=True, nullable=False)
    Phone_Number = db.Column(db.String(18), unique=True, nullable=False)

    def __repr__(self):
        return '{<Firstname %r>, <LastName %r>, <Sexe %r>, <Email %r>, <Password %r>, <CIN %r>, <PHONE %r>}' % (self.FirstName, self.LastName, self.Sexe, self.Email, self.Password, self.CIN, self.Phone_Number)


####################
@app.route('/')
def hello():
    return render_template('home.html')


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup/submit', methods=['POST'])
def register_user():
    
    user_FN = request.form['FirstName']
    user_LN = request.form['LastName']
    user_GENDER = request.form['gender']
    user_EMAIL = request.form['email']
    user_PASS = request.form['password']
    user_PHONE = request.form['phone']
    user_CIN = request.form['cin']

    CheckCIN = User_data.query.filter_by(CIN = user_CIN).first()
    CheckPHONE = User_data.query.filter_by(Phone_Number = user_PHONE).first()

    if CheckCIN:
        flash("le CIN deja utiliser")
        return redirect(url_for('signup'))

    elif CheckPHONE:
        flash("le Numero deja utiliser")
        return redirect(url_for('signup'))
    
    else:
        user = User_data(FirstName = user_FN, LastName = user_LN, Sexe = user_GENDER, Email = user_EMAIL, Password = generate_password_hash(user_PASS, method='sha256'), CIN = user_CIN, Phone_Number = user_PHONE)
        
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

@app.route('/login/submit', methods=['POST'])
def login_post():
    user_CIN = request.form['CIN']
    user_PASS = request.form['password']

    Checkuser = User_data.query.filter_by(CIN = user_CIN).first()

    if not Checkuser or not check_password_hash(Checkuser.Password, user_PASS):
        flash('verifier votre login detailles')
        return redirect(url_for('login'))

    return render_template('dashboard.html', name = Checkuser.FirstName)
    




    

if __name__ == '__main__':
    app.run(debug=True)