from flask import Flask, render_template, request, session, redirect, url_for
from forms import SignupForm, LoginForm, InvestForm, LoanForm

import os
import pyrebase
import json
import openpay

config = {
  "apiKey": "AIzaSyBgbGvUXaV2Npjvr5A04AW48TwSpJvouuI",
  "authDomain": "project-7682141674235767650.firebaseapp.com",
  "databaseURL": "https://kinto.firebaseio.com",
  "storageBucket": "project-7682141674235767650.appspot.com"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
db = firebase.database()

app = Flask(__name__)

app.secret_key = "development-key"

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
            email = form.email.data
            password = form.password.data
            
            user = auth.sign_in_with_email_and_password(email, password)
            userIdToken = user['idToken']
            session["email"] = email
            session["idToken"] = userIdToken
            return redirect(url_for('home'))
            
    elif request.method == "GET":
        return render_template("login.html", form = form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    
    if request.method == "POST":
        if form.validate() == False:
            return render_template('signup.html', form = form)
        else :
            user = auth.create_user_with_email_and_password(form.email.data, form.password.data)
            #auth.send_email_verification(user['idToken'])
            session["email"] = form.email.data
            session["idToken"] = user['idToken']
            return redirect(url_for("home"))
    
    elif request.method == "GET":
        return render_template("signup.html", form = form)


@app.route("/home")
def home():
    return render_template("home.html")

    
@app.route("/mov")
def mov():
    return render_template("mov.html")

    
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
        db.child("invests").child(email).push(data)
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
        db.child("/invests/"+email).push(data)
        return render_template("loan.html", form = form)


@app.route("/support")
def support():
    return render_template("support.html")
    
@app.route("/logout")    
def logout():
    session.pop('email', None)
    session.pop('idToken', None)
    return redirect((url_for("index")))
    
if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
