from flask import Flask, render_template, request, session, redirect, url_for
from forms import SignupForm, LoginForm

import os
import pyrebase
import json
#import openpay

config = {
  "apiKey": "AIzaSyBgbGvUXaV2Npjvr5A04AW48TwSpJvouuI",
  "authDomain": "project-7682141674235767650.firebaseapp.com",
  "databaseURL": "https://kinto.firebaseio.com",
  "storageBucket": "project-7682141674235767650.appspot.com"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()

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
            return render_template("login.html", form=form)
        else:
            email = form.email.data
            password = form.password.data
            
            user = auth.sign_in_with_email_and_password(email, password)
            if user["errors"] :
                return "Error"
            else :
                userIdToken = user['idToken']
                return userIdToken
            
            #return redirect(url_for("home"))
            
    elif request.method == "GET":
        return render_template("login.html", form = form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    
    if request.method == "POST":
        if form.validate() == False:
            return render_template('signup.html', form = form)
        else :
            auth.create_user_with_email_and_password(form.email.data, form.password.data)
            auth.send_password_reset_email(form.email.data)
            session["email"] = form.email.data
            return redirect(url_for("home"))
    
    elif request.method == "GET":
        return render_template("signup.html", form = form)


@app.route("/home")
def home():
    return render_template("home.html")

    
@app.route("/mov")
def mov():
    return render_template("mov.html")

    
@app.route("/invest")
def invest():
    return render_template("invest.html")

    
@app.route("/loan")
def loan():
    return render_template("loan.html")


@app.route("/support")
def support():
    return render_template("support.html")
    
    
if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
