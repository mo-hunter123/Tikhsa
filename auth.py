from flask import Blueprint, redirect, render_template, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User_data
from flask_login import login_required, current_user, UserMixin, LoginManager, login_user, logout_user
from . import db
from flask_sqlalchemy import SQLAlchemy


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup/submit', methods=['POST'])
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
    CheckEMAIL = User_data.query.filter_by(Email = user_EMAIL).first()

    if user_GENDER == 'Choisir...':
        flash("enter a gender")
        return redirect(url_for('auth.signup'))

    if CheckEMAIL:
        flash("l'Email' deja utiliser")
        return redirect(url_for('auth.signup'))


    if CheckCIN:
        flash("le CIN deja utiliser")
        return redirect(url_for('auth.signup'))

    elif CheckPHONE:
        flash("le Numero deja utiliser")
        return redirect(url_for('auth.signup'))
    
    user = User_data(FirstName = user_FN, LastName = user_LN, Sexe = user_GENDER, Email = user_EMAIL, Password = generate_password_hash(user_PASS, method='sha256'), CIN = user_CIN, Phone_Number = user_PHONE)
    
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/login/submit', methods=['POST', 'GET'])
def login_sub():
    if request.method == 'POST':
               
        user_CIN = request.form['CIN']
        user_PASS = request.form['password']

        Checkuser = User_data.query.filter_by(CIN = user_CIN).first()

        if not Checkuser or not check_password_hash(Checkuser.Password, user_PASS):
            flash('verifier votre login detailles')
            return redirect(url_for('auth.login'))

        login_user(Checkuser)
        return redirect(url_for('main.profile'))
    
    else:
        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
    
