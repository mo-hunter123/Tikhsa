from flask import Flask, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user, UserMixin, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os




app = Flask(__name__)

# app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userDa.db'

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

######## models



class User_data(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(80), nullable=False)
    LastName = db.Column(db.String(80), nullable=False)
    Sexe = db.Column(db.String(18), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password = db.Column(db.String(18), unique=True, nullable=False)
    CIN = db.Column(db.String(18), unique=True, nullable=False)
    Phone_Number = db.Column(db.String(18), unique=True, nullable=False)

    def __repr__(self):
        return '{<Firstname %r>, <LastName %r>, <Sexe %r>, <Email %r>, <Password %r>, <CIN %r>, <PHONE %r>}' % (self.FirstName, self.LastName, self.Sexe, self.Email, self.Password, self.CIN, self.Phone_Number)


# class Facture(UserMixin, db.Model):


########

@login_manager.user_loader
def load_user(user_id):
    return User_data.query.get(int(user_id))

####### main

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('dashboard.html', current_user = current_user)

########

####### auth

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        
        user_FN = request.form['FirstName']
        user_LN = request.form['LastName']
        user_GENDER = request.form['gender']
        user_EMAIL = request.form['email']
        user_PASS = request.form['password']
        user_PHONE = request.form['phone']
        user_CIN = request.form['cin']

        CheckCIN = User_data.query.filter_by(CIN = user_CIN).first()
        CheckPHONE = User_data.query.filter_by(Phone_Number = user_PHONE).first()
        CheckEMAIL = User_data.query.filter_by(Email = user_EMAIL).first()

        if user_GENDER == 'Choisir...':
            flash("enter a gender")
            return redirect(url_for('signup'))

        if CheckEMAIL:
            flash("l'Email' deja utiliser")
            return redirect(url_for('signup'))


        if CheckCIN:
            flash("le CIN deja utiliser")
            return redirect(url_for('signup'))

        elif CheckPHONE:
            flash("le Numero deja utiliser")
            return redirect(url_for('signup'))
        
        user = User_data(FirstName = user_FN, LastName = user_LN, Sexe = user_GENDER, Email = user_EMAIL, Password = generate_password_hash(user_PASS, method='sha256'), CIN = user_CIN, Phone_Number = user_PHONE)
        
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    
    if request.method == 'GET' and current_user.is_authenticated:
        return redirect('/')

    else:
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
               
        user_CIN = request.form['CIN']
        user_PASS = request.form['password']

        Checkuser = User_data.query.filter_by(CIN = user_CIN).first()

        if not Checkuser or not check_password_hash(Checkuser.Password, user_PASS):
            flash('verifier votre login detailles')
            return redirect(url_for('login'))

        login_user(Checkuser)
        return redirect(url_for('profile'))
    
    if request.method == 'GET' and current_user.is_authenticated:
        return redirect('profile')

    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
    

######

if __name__ == '__main__':
    app.run(debug=True)
