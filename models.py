from flask_login import UserMixin
from . import db


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
