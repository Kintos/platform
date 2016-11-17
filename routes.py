from flask import Flask, render_template, request, session, redirect, url_for
from forms import SignupForm, LoginForm, InvestForm, LoanForm, RecoverForm
from requests.exceptions import HTTPError

import os
import json
import openpay
import pyrebase

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
                userIdToken = user['idToken']
                session["email"] = email
                session["idToken"] = userIdToken
                return redirect(url_for('home'))
            except HTTPError as e:
                print("Authentication error")
                return render_template("login.html", form=form, message = "Por favor revise sus datos")
                #return redirect(url_for('login'))
            
    elif request.method == "GET":
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
                auth.send_email_verification(user['idToken'])
                session["email"] = form.email.data
                session["idToken"] = user['idToken']
                return redirect(url_for("home"))
            except HTTPError as e:
                print(e.args())
                return render_template("signup.html", form = form, message = "Ese correo ya esta registrado")
                
    elif request.method == "GET":
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
        return render_template("home.html")
    else :
        return redirect(url_for("index"))
        
@app.route("/mov")
def mov():
    if "email" in session :
        return render_template("mov.html")
    else :
        return redirect(url_for("index"))
    
@app.route("/invest", methods=["GET", "POST"])
def invest():
    form = InvestForm()
    if request.method == "POST":
        email = session["email"]
        amount = request.form.get('amount')
        duration = request.form.get('duration')
        total = request.form.get('total')
        data = {'amount':amount, 'duration': duration, 'total':total }
        data = json.dumps(data, ensure_ascii=False)
        #data = {"name": "Mortimer 'Morty' Smith"}
        db.child("users").push(data)

        return "done!"
        #token = session("idToken")
    elif request.method == "GET":
        if "email" in session :
            return render_template('invest.html', form = form)
        else :
            return redirect(url_for("index"))
    
@app.route("/loan",  methods=["GET", "POST"])
def loan():
    form = LoanForm()
    if request.method == "POST":
        email = session["email"]
        amount = request.form.get('amount')
        duration = request.form.get('duration')
        total = request.form.get('total')
        data = {'amount':amount, 'duration': duration, 'total':total }
        data = json.dumps(data, ensure_ascii=False)
        db.child("invests").child(email).push(data)
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
    session.pop('idToken', None)
    return redirect((url_for("index")))
    
if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
