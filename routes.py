from flask import Flask, render_template, request, session, redirect, url_for
from forms import SignupForm, LoginForm, InvestForm, LoanForm, RecoverForm
from requests.exceptions import HTTPError
from collections import OrderedDict

import os
import json
import openpay
import pyrebase
import datetime

config = {
  "apiKey": "AIzaSyBgbGvUXaV2Npjvr5A04AW48TwSpJvouuI",
  "authDomain": "project-7682141674235767650.firebaseapp.com",
  "databaseURL": "https://kinto.firebaseio.com",
  "storageBucket": "project-7682141674235767650.appspot.com",
  "serviceAccount":"./kintos-83468dd3a92e.json"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
db = firebase.database()

app = Flask(__name__)

#randome secret development key
app.secret_key = "b'\x82\xddj\x06\x9bm\x06\xca,{\xb3\xee\xb0\x82\xbf_\x87x\x10\x9e\xd5f\xd3\xb8'"

openpay.api_key = "sk_34205741f0144b0a864309ec3f7b5267"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mompk30sik9s5j8x0pmf"
openpay.production = False  # By default this works in sandbox mode

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate() == False:
            return render_template("login.html", form = form)
        else:
            try:
                email = form.email.data
                password = form.password.data
                user = auth.sign_in_with_email_and_password(email, password)
                session["email"] = email
                session["localId"] = user['localId']
                info = db.child("users").child(session["localId"]).get()
                info = info.val()
                session["fname"] = info['fname']
                session["lname"] = info['lname']
                return redirect(url_for('home'))
            except HTTPError as e:
                print("Authentication error")
                return render_template("login.html", form=form, message = "Por favor revise sus datos")
            
    elif request.method == "GET":
        if "email" in session:
            return redirect(url_for("home"))
        else:
            return render_template("login.html", form = form)
            

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    
    if request.method == "POST":
        if form.validate() == False:
            return render_template('signup.html', form = form)
        else :
            try:
                user = auth.create_user_with_email_and_password(form.email.data, form.password.data)
                #auth.send_email_verification(user['idToken'])
                session["email"] = form.email.data
                session["localId"] = user['localId']
                session["fname"] = form.first_name.data
                session["lname"] = form.last_name.data
                data = {
                        'fname': form.first_name.data,
                        'lname': form.last_name.data,
                        'email': form.email.data
                        }
                customer = openpay.Customer.create(
                    name = form.first_name.data,
                    last_name = form.last_name.data,
                    email = form.email.data,
                    phone_number="44209087654"
                )                        
                db.child("users").child(session["localId"]).set(data)
                return redirect(url_for("home"))
            except HTTPError as e:
                print(e.args())
                return render_template("signup.html", form = form, message = "Ese correo ya esta registrado")
                
    elif request.method == "GET":
        if "email" in session:
            return redirect(url_for("home"))
        else:
            return render_template("signup.html", form = form)
        

@app.route("/recover", methods=["POST", "GET"])
def recover():
    form = RecoverForm()
    if request.method == "POST":
        if form.validate() == False:
            return render_template("recover.html", form = form)
        else:
            try:
                email = form.email.data
                auth.send_password_reset_email(email)
                return render_template("recover.html", form=form, message = "Correo de recuperacion enviado")
            except HTTPError as e:
                print("Email error")
                return render_template("recover.html", form=form, message = "Correo no valido")
    elif request.method == "GET":
        return render_template("recover.html", form = form)

@app.route("/home")
def home():
    if "email" in session :
        loan = db.child('loans').child(session['localId']).get().val()
        invest = db.child('invests').child(session['localId']).get().val()
        if loan is not None :
            loan = len(loan)
        if invest is not None :
            invest = len(invest)
        return render_template("home.html", loan = loan, invest = invest, name = session["fname"])
    else :
        return redirect(url_for("index"))
        
@app.route("/mov")
def mov():
    if "email" in session :
        loans = db.child('loans').child(session['localId']).get().val()
        invests = db.child('invests').child(session['localId']).get().val()
        loans = list(loans.items())
        invests = list(invests.items())
        for invest in invests:
            print(invest[1]['total'])
        print(loans)
        #data = json.loads(loans, object_pairs_hook=OrderedDict)
        return render_template("mov.html", invests = invests, loans = loans)
    else :
        return redirect(url_for("index"))
    
@app.route("/invest", methods=["GET", "POST"])
def invest():
    form = InvestForm()
    if request.method == "POST":
        try:
            current = datetime.datetime.now()
            amount = request.form.get('amount')
            duration = request.form.get('duration')
            pagoSemanal = request.form.get('total')
            total = float(pagoSemanal) * float(duration)
            data = {'amount':amount, 
                    'duration': duration, 
                    'total':total,
                    'pagoSemanal': pagoSemanal,
                    'state': 'Pago pendiente',
                    'date': current.strftime("%d-%m-%Y %H:%M")
                    }
            db.child("invests").child(session['localId']).push(data)
            return render_template("invest.html", form=form, investAccepted = "Prestamo realizado de manera correcta")
        except HTTPError as e:
            return render_template("invest.html", form = form, message = "Se presento un error al realizar la operacion")
    elif request.method == "GET":
        if "email" in session :
            return render_template('invest.html', form = form)
        else :
            return redirect(url_for("index"))
    
@app.route("/loan",  methods=["GET", "POST"])
def loan():
    form = LoanForm()
    if request.method == "POST":
        try:
            current = datetime.datetime.now()
            email = session["email"]
            amount = request.form.get('amount')
            duration = request.form.get('duration')
            pagoSemanal = request.form.get('total')
            total = float(duration) * float(pagoSemanal)
            data = {'amount':amount, 
                    'duration': duration, 
                    'total':total,
                    'pagoSemanal': pagoSemanal,
                    'state': 'Pago pendiente',
                    'date': current.strftime("%d-%m-%Y %H:%M")
                    }
            db.child("loans").child(session['localId']).push(data)
            return render_template("loan.html", form=form, loanAccepted = "Prestamo realizado de manera correcta")
        except:
            return render_template("loan.html", form=form, message = "Se presento un error al realizar la operacion")
    elif request.method == "GET":
        if "email" in session :
            return render_template('loan.html', form = form)
        else :
            return redirect(url_for("index"))

@app.route("/support")
def support():
    if "email" in session :
        return render_template("support.html")
    else :
        return redirect(url_for("index"))
        
@app.route("/settings")
def settings():
    if "email" in session :
        return render_template("settings.html")
    else :
        return redirect(url_for("index"))        
        
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404        
    
@app.route("/logout")    
def logout():
    session.pop('email', None)
    return redirect((url_for("index")))
    
if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
