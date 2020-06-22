import os
from flask import Flask
from flask import Blueprint, request, render_template, redirect, flash, url_for
from flask_login import login_required, current_user


main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('dashboard.html', name=current_user.FirstName)


