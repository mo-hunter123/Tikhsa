import os
from flask import Flask
from flask import request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TEST_Usrs.db'

# app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)


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

if __name__ == '__main__':
    app.run()