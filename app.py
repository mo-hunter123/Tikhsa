from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import login_required, current_user, UserMixin, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
from sqlalchemy.dialects.postgresql import JSON


app = Flask(__name__)

# app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///updated.db'

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

######## models #########

# class Douar(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Douar_Name = db.Column(db.String(90), nullable = False, unique = True)
#     Associations = db.relationship('Association', backref='douar', lazy=True)


# class Association(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Asso_Name = db.Column(db.String(90), nullable = False, unique = True)
#     douar_id = db.Column(db.Integer, db.ForeignKey('douar.id'))
#     services = db.relationship('service', backref='association', lazy=True)


# class service(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     service_Name = db.Column(db.String(90), nullable = False, unique = True)
#     asso_id = db.Column(db.Integer, db.ForeignKey('association.id'))

class admin(UserMixin, db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(80), nullable=False)
    PassW = db.Column(db.String(200), nullable=False)
    releves = db.relationship('RelevesCompteur', backref='admin', lazy=True)
    Compteurs = db.relationship('Compteurinfo', backref='admin', lazy=True)

    def __repr__(self):
        return 'Admin : %r ' % self.Username
    
class Person(UserMixin, db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    FirstName = db.Column(db.String(80), nullable=False)
    LastName = db.Column(db.String(80), nullable=False)
    Sexe = db.Column(db.String(18), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password = db.Column(db.String(200), unique=True, nullable=False)
    CIN = db.Column(db.String(18), unique=True, nullable=False)
    Phone_Number = db.Column(db.String(18), unique=True, nullable=False)
    Date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    Compteurs = db.relationship('Compteurinfo', backref='person', lazy=True)

    def __repr__(self):
        return '<%r - %r - %r - %r - %r - %r>' % (self.id, self.FirstName, self.LastName, self.CIN, self.Phone_Number, self.Email)

class Compteurinfo(db.Model):
    __tablename__ = 'compteurinfo'

    id = db.Column(db.Integer, primary_key=True)
    Code_Compteur = db.Column(db.Integer, nullable = False, unique = True)
    #owner de compteur
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    DateInstallation = db.Column(db.DateTime, nullable = False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    Date_created = db.Column(db.DateTime, nullable = False, default = datetime.datetime.utcnow)
    relcompteurs = db.relationship('RelevesCompteurDetails', backref='compteur', lazy=True)
    factures = db.relationship('Factures', backref='compteur', lazy=True)

    def __repr__(self):
        return '<%r - %r - %r>' % (self.id, self.Code_Compteur, self.person_id)

class RelevesCompteur(db.Model):
    __tablename__ = 'relevescompteur'

    id = db.Column(db.Integer, primary_key=True)
    DateSaisie = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    DateActuelle = db.Column(db.DateTime, nullable=False)
    DatePrecedente = db.Column(db.DateTime, nullable=False)
    NombreMois = db.Column(db.Integer, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    indicationReleve = db.Column(db.String(80), default='test it')
    detail = db.relationship('RelevesCompteurDetails', uselist=False, backref='releve')
    factures = db.relationship('Factures', backref='releve')

    def __repr__(self):
        return '<%r - %r - %r - %r>' % (self.id, self.NombreMois, self.admin_id, self.indicationReleve)

class RelevesCompteurDetails(db.Model):
    __tablename__ = 'relevescompteurdetails'

    id = db.Column(db.Integer, primary_key=True)
    rel_id = db.Column(db.Integer, db.ForeignKey('relevescompteur.id'))
    compteur_id = db.Column(db.Integer, db.ForeignKey('compteurinfo.id'))
    consommationPrecedente = db.Column(db.Integer, nullable=False, default = 0)
    consommationActuelle = db.Column(db.Integer, nullable=False)
    commentaire = db.Column(db.String(500), nullable=False, default="pas de commentaire pour ce compteur")

    def __repr__(self):
        return '<%r - %r - %r - %r - %r>' % (self.rel_id, self.compteur_id, self.consommationPrecedente, self.consommationActuelle, self.commentaire)

class Factures(db.Model):
    __tablename__ = 'factures'

    id = db.Column(db.Integer, primary_key=True)
    rel_id = db.Column(db.Integer, db.ForeignKey('relevescompteur.id'))
    Date_facture = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    Montant_facture = db.Column(db.Integer, nullable=False)
    generated = db.Column(db.Boolean, nullable = False, default = False)
    compteur_id = db.Column(db.Integer, db.ForeignKey('compteurinfo.id'))

    def __repr__(self):
        return '<%r - %r - %r - %r>' % (self.rel_id, self.Montant_facture, self.generated, self.compteur_id)

########

@login_manager.user_loader
def load_user(admin_id):
    return admin.query.get(int(admin_id))

####### main
def deleteRel(id):
    Factures.query.filter_by(rel_id = id).delete()
    RelevesCompteurDetails.query.filter_by(rel_id = id).delete()
    RelevesCompteur.query.filter_by(id = id).delete()
    
    db.session.commit()

@app.route('/deleteid/<int:relid>')
@login_required
def deleteid(relid):
    x = RelevesCompteur.query.filter_by(id = (int(relid)+1)).first()
    if x:
        flash('you can t delete this one')
        return redirect(url_for('adminpannel'))


    deleteRel(relid)

    flash('Rele succefully deleted')
    return redirect(url_for('adminpannel'))

@app.route('/')
@app.route('/home')
def home():
    
    return redirect('adminpannel')

@app.route('/adminpannel')
@login_required
def adminpannel():
    users = db.session.query(Person).all()
    compteurs = db.session.query(Compteurinfo).all()
    l = len(compteurs)
    releves = db.session.query(RelevesCompteur).all()
    relevesDet = db.session.query(RelevesCompteurDetails).all()

    
    return render_template('AdminPannel.html', releves = releves, relevesDet = relevesDet, users = users, compteurs = compteurs, datetime = datetime)

########person_id = 1, consommatperson_id = 1, consommation=reqion=req

####### auth

@app.route('/signup', methods=['POST', 'GET'])
@login_required
def signup():
    if request.method == 'POST':
        
        
        user_FN = request.form['FirstName']
        user_LN = request.form['LastName']
        user_GENDER = request.form['gender']
        user_EMAIL = request.form['email']
        user_PASS = request.form['password']
        user_PHONE = request.form['phone']
        user_CIN = request.form['code']
        user_Status = request.form['gridRadios']

        CheckCIN = Person.query.filter_by(CIN = user_CIN).first()
        CheckPHONE = Person.query.filter_by(Phone_Number = user_PHONE).first()
        CheckEMAIL = Person.query.filter_by(Email = user_EMAIL).first()

        if user_GENDER == 'Choisir...':
            flash("enter a gender")
            return redirect(url_for('signup'))

        if CheckEMAIL:
            flash("l'Email' deja utiliser")
            return redirect(url_for('signup'))


        if CheckCIN:
            flash("le Code deja utiliser")
            return redirect(url_for('signup'))

        elif CheckPHONE:
            flash("le Numero deja utiliser")
            return redirect(url_for('signup'))
        
        user = Person(FirstName = user_FN, LastName = user_LN, Sexe = user_GENDER, Email = user_EMAIL, Password = generate_password_hash(user_PASS, method='sha256'), CIN = user_CIN, Phone_Number = user_PHONE, status = user_Status)
        
        db.session.add(user)
        db.session.commit()

        return redirect('adminpannel') 
    else:
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
               
        user_Name = request.form['username']
        user_PASS = request.form['password']

        Checkuser = admin.query.filter_by(Username = user_Name).first()

        if not Checkuser or not (Checkuser.PassW == user_PASS):
            flash('verifier votre login detailles')
            return redirect(url_for('login'))

        login_user(Checkuser)
        return redirect(url_for('adminpannel'))

    else:
        if current_user.is_authenticated:
            return redirect(url_for('adminpannel'))

        return render_template('login.html')

@app.route('/adminpannel/users/<int:id>')
@login_required
def userProfile(id):
    #pour le moment on suppose que chaque utilisateur a un seul compteur 
    compteur = Compteurinfo.query.filter_by(person_id = id).first()
    factures = Factures.query.filter_by(compteur_id = compteur.id).all()

    
    return render_template('profile.html', compteur = compteur, factures = factures)

    
@app.route('/addrelev', methods=['POST', 'GET'])
@login_required
def addrelev():
    if request.method == 'POST':
        
        
        j = request.form['jour']
        m = request.form['mois']
        an = request.form['annee']

        rel_title = request.form['titlerel']

        try:
            x = datetime.datetime(int(an), int(m), int(j))

        except ValueError:

            flash('certainne de vos valeurs est fausse')
            return redirect('addrelev')

        if x.day != 1:
            flash('la date doit etre egale au premier du mois')
            return redirect('addrelev')


        a = db.session.query(Compteurinfo).all()
        b = db.session.query(RelevesCompteur).all()

        if b:
            ii = RelevesCompteurDetails.query.filter_by(rel_id = b[len(b)-1].id).all()

            y = RelevesCompteur.query.filter_by(id = b[len(b) - 1].id).first()

            if len(ii) == len(a):
                if y.DateActuelle >= x:

                    flash('verifier votre Date de Saisie')
                    return redirect('addrelev')

                d = x - y.DateActuelle
                rel_Mois = int(d.days/28)

                if rel_Mois < 1:
                    flash('la duree entre les releves faut etre superieur a un mois')
                    return redirect('addrelev')

                rel = RelevesCompteur(admin_id = current_user.id, DatePrecedente = y.DateActuelle, DateActuelle = x, indicationReleve = rel_title, NombreMois = rel_Mois)

                db.session.add(rel)
                db.session.commit()
                
                return redirect('showrelev/'+str(rel.id))
            
            else:
                flash('il s emble comme si vous n avez pas bien remplis votre dernier releve')
                return redirect('addrelev')

        else:
            rel_Mois = 1
            rel = RelevesCompteur(admin_id = current_user.id, DatePrecedente = datetime.datetime(2018, 5, 1), DateActuelle = x, indicationReleve = rel_title, NombreMois = rel_Mois)

            db.session.add(rel)
            db.session.commit()
            return redirect('showrelev/'+str(rel.id))

        
    else:
        compteurs = db.session.query(Compteurinfo).all()
        if compteurs:
            return render_template('AddRelev.html')

        else:
            flash('ajouter un compteur premierement')
            return redirect(url_for('adminpannel'))


@app.route('/addcompteur', methods=['POST', 'GET'])
@login_required
def addcompteur():
    if request.method == 'POST':
        co_co = request.form['code']
        id_pe = request.form['idPerson']

        j = request.form['jour']
        m = request.form['mois']
        a = request.form['annee']

        try:
            x = datetime.datetime(int(a), int(m), int(j))

        except ValueError:
            flash('certainne de vos valeurs est fausse')
            return redirect('addcompteur')
        
        

        check = Compteurinfo.query.filter_by(Code_Compteur = co_co).first()
            
        if check:
            flash('ce compteur existe deja')
            return redirect(url_for('addcompteur'))

        if co_co == '' or id_pe == '':
            flash('un des champs est vide')
            return redirect(url_for('addcompteur'))

        compteur = Compteurinfo(Code_Compteur = co_co, person_id = id_pe, DateInstallation = x, admin_id = current_user.id)
        db.session.add(compteur)
        db.session.commit()
        flash('le compteur bien ajoute')

        return redirect(url_for('adminpannel'))

    else:
        users = db.session.query(Person).all()
        compteurs = db.session.query(Compteurinfo).all()
        return render_template('AddCompteur.html', users = users, compteurs = compteurs)

@app.route('/showrelev/<int:id>', methods=['POST', 'GET'])
@login_required
def showrelev(id):
    if request.method == 'POST':

        relId = request.form['rel_id']
        compteurId = request.form['compteur_id']

        compteur_con = request.form['consommation']
        comment = request.form['comment']

        a = RelevesCompteurDetails.query.filter_by(compteur_id = compteurId).all()

        if not a:
            Ucon = RelevesCompteurDetails(consommationActuelle = compteur_con, commentaire = comment, rel_id = relId, compteur_id = compteurId, consommationPrecedente = 0)
            db.session.add(Ucon)
            db.session.commit()

            flash('les detailles de rel bien ajouter')
            return redirect(url_for('showrelev', id = relId))

        else:
            a = db.session.query(RelevesCompteur).all()
        
            ch = RelevesCompteurDetails.query.filter_by(rel_id = a[len(a) - 2].id, compteur_id = compteurId).first()
            c = RelevesCompteurDetails.query.filter_by(rel_id = relId, compteur_id = compteurId).first()

            if c:
                flash('le compteur qui vous faire ajouter existe deja')
                return redirect(url_for('showrelev', id = relId))


            compteur_con = request.form['consommation']
            comment = request.form['comment']
            
            if int(compteur_con) <= ch.consommationActuelle:
                flash(ch.consommationActuelle)
                flash('m (cube): est la consommation precedente .. verifier vos donnees')
                return redirect(url_for('showrelev', id = relId))

            
            Ucon = RelevesCompteurDetails(consommationActuelle = compteur_con, commentaire = comment, rel_id = relId, compteur_id = compteurId, consommationPrecedente = ch.consommationActuelle)
            db.session.add(Ucon)
            db.session.commit()
                
            flash('les detailles de rel bien ajouter')
            return redirect(url_for('showrelev', id = relId))

    else:
        
        releve = RelevesCompteur.query.filter_by(id = id).first()
        releveDet = RelevesCompteurDetails.query.filter_by(rel_id = id).all()
        compteurs = db.session.query(Compteurinfo).all()
        users = db.session.query(Person).all()
        factures = Factures.query.filter_by(rel_id = id).all()
        return render_template('ShowRelev.html', releve = releve, releveDet = releveDet, compteurs = compteurs, users = users, factures = factures, len = len)

@app.route('/showrelev/<int:idrel>/facture/<int:idcompteur>', methods=['POST', 'GET'])
@login_required
def factureid(idrel, idcompteur):
    if request.method == 'POST':

        a = db.session.query(Compteurinfo).all()
        b = db.session.query(RelevesCompteur).all()

        if b:
            ii = RelevesCompteurDetails.query.filter_by(rel_id = b[len(b)-1].id).all()

            if len(ii) == len(a):
                a1 = RelevesCompteurDetails.query.filter_by(rel_id = idrel).all()

                a2 = RelevesCompteur.query.filter_by(id = idrel).first()

                montant1 = (a1[idcompteur-1].consommationActuelle - a1[idcompteur-1].consommationPrecedente)*5
                montant2 = a2.NombreMois * 10

                Tot = max(montant1, montant2)

                fac = Factures(rel_id = idrel, Montant_facture = Tot, compteur_id = idcompteur, generated = True)

                db.session.add(fac)
                db.session.commit()
                
                return redirect(url_for('showrelev', id = idrel))
            
            else:
                flash('il s emble comme si vous n avez pas bien remplis votre dernier releve')
                return redirect(url_for('showrelev', id = idrel))

    else:
        f = Factures.query.filter_by(rel_id = idrel, compteur_id = idcompteur).first()
        r = RelevesCompteurDetails.query.filter_by(rel_id = idrel, compteur_id = idcompteur).first()
        c = Compteurinfo.query.filter_by(id = idcompteur).first()
        i = RelevesCompteur.query.filter_by(id = idrel).first()
        p = Person.query.filter_by(id = c.person_id).first()

        return render_template('facture.html', f = f, i = i, r = r, c = c, p = p, datetime = datetime)



@app.route('/showrelev/<int:idrel>/update/<int:idcompteur>', methods=['POST', 'GET'])
@login_required
def updateid(idrel, idcompteur):
    if request.method == 'POST':
        d = Factures.query.filter_by(rel_id = idrel, compteur_id = idcompteur).first()

        if d.generated:
            flash('la facture de ce releve existe deja alors vous ne pouvez pas mis a jour les donnees')
            return redirect(url_for('showrelev', id = idrel))

        else:
            a = RelevesCompteurDetails.query.filter_by(rel_id = idrel, compteur_id = idcompteur).first()
            a.consommationActuelle = request.form['consommation']
            db.session.commit()

        return redirect(url_for('showrelev', id = idrel))
        
    else:
        a1 = RelevesCompteurDetails.query.filter_by(rel_id = idrel, compteur_id = idcompteur).first()
        return render_template('updateRel.html', a1 = a1)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    
######

if __name__ == '__main__':
    app.run(debug=True)
