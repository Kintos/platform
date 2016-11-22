import os
import json
import openpay
import pyrebase
import datetime

from flask import Flask, render_template, request, session, redirect, url_for
from forms import SignupForm, LoginForm, InvestForm, LoanForm, RecoverForm, settingsForm
from requests.exceptions import HTTPError
from openpay import error as openpayError


firebaseConfig = {
  "apiKey": "AIzaSyBgbGvUXaV2Npjvr5A04AW48TwSpJvouuI",
  "authDomain": "project-7682141674235767650.firebaseapp.com",
  "databaseURL": "https://kinto.firebaseio.com",
  "storageBucket": "project-7682141674235767650.appspot.com",
  "serviceAccount":"./kintos-83468dd3a92e.json"
}

firebase = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()
db = firebase.database()

app = Flask(__name__)

#randome secret development key
app.secret_key = "b'\x82\xddj\x06\x9bm\x06\xca,{\xb3\xee\xb0\x82\xbf_\x87x\x10\x9e\xd5f\xd3\xb8'"

openpay.api_key = "sk_34205741f0144b0a864309ec3f7b5267"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mompk30sik9s5j8x0pmf"
openpay.production = False  # By default this works in sandbox mode

def expFaltante(nivel, exp):
    if nivel == 1:
        result = "Experiencia faltante para el siguiente nivel:  " + str(500 - exp)
    elif nivel == 2:
        result = "Experiencia faltante para el siguiente nivel: " + str(1000 - exp)
    elif nivel == 3:
        result = "Experiencia faltante para el siguiente nivel: " + str(2000 - exp)
    elif nivel == 4:
        result =  "Experiencia faltante para el siguiente nivel: " + str(4000 - exp)
    elif nivel == 0:
        result = "Tienes que terminar el registro en configuracion para poder subir de nivel"
    else:
        result = "Felicidades haz alcanzado el nivel maximo"
    return result
    
def gamification(nivel, exp):
    print(nivel, exp)
    if nivel == 1:
        print("si entro")
        if exp >= 500:
            session["level"] = 2
            session["exp"] = exp - 500
        else:
            session["exp"] = exp
            print("hola")
    elif nivel == 2:
        if exp >= 1000:
            session["level"] = 3
            session["exp"] = exp - 1000
        else:
            session["exp"] = exp
    elif nivel == 3:
        if exp >= 2000:
            session["level"] = 4
            session["exp"] = exp - 2000
        else:
            session["exp"] = exp
    elif nivel == 4:
        if exp >= 4000:
            session["level"] = 5
            session["exp"] = 0
        else:
            session["exp"] = exp
    else:
        return 0

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
                info = db.child("users").child(session["localId"]).get().val()
                session["fname"] = info['fname']
                session["lname"] = info['lname']
                session["level"] = info["level"]
                session["exp"] = info["exp"]
                session["openpay_id"] = info["openpay_id"]
                session["openpay_clabe"] = info["openpay_clabe"]
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
        else:
            try:
                user = auth.create_user_with_email_and_password(form.email.data, form.password.data)
                #auth.send_email_verification(user['idToken'])
                customer = openpay.Customer.create(
                    name = form.first_name.data,
                    last_name = form.last_name.data,
                    email = form.email.data,
                    phone_number = form.phone.data
                )
                session["email"] = form.email.data
                session["localId"] = user['localId']
                session["fname"] = form.first_name.data
                session["lname"] = form.last_name.data
                session["level"] = 0
                session["exp"] = 0
                session["openpay_id"] = customer["id"]
                session["openpay_clabe"] = customer["clabe"]
                data = {
                        'fname': form.first_name.data,
                        'lname': form.last_name.data,
                        'email': form.email.data,
                        'phone': form.phone.data,
                        'openpay_id': customer["id"],
                        'openpay_clabe': customer["clabe"],
                        'state' : 'Regular',
                        'debt': 0,
                        'level': 0,
                        'exp': 0
                        }
                db.child("users").child(session["localId"]).set(data)
                return redirect(url_for("home"))
            except HTTPError as e:
                #print(e.args())
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
            
        exp = expFaltante(session["level"], session["exp"])
        return render_template("home.html", loan = loan, invest = invest, name = session["fname"], nivel = session["level"], exp = exp)
    else :
        return redirect(url_for("index"))
        
@app.route("/mov")
def mov():
    if "email" in session :
        loans = db.child('loans').child(session['localId']).get().val()
        invests = db.child('invests').child(session['localId']).get().val()
        
        if loans is not None :
            loans = list(loans.items())
        if invests is not None :
            invests = list(invests.items())

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
                    'state': 'pago pendiente',
                    'date': current.strftime("%d-%m-%Y %H:%M")
                    }
            newexp = int(session["exp"]) + 250
            gamification(session["level"], newexp)
            db.child("users").child(session["localId"]).update({"level": session["level"]})
            db.child("users").child(session["localId"]).update({"exp": session["exp"]})
            db.child("invests").child(session['localId']).push(data)

            return render_template("invest.html", form=form, investAccepted = "Inversion realizado de manera correcta")
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
            data = {
                    'amount':amount, 
                    'duration': duration, 
                    'total':total,
                    'pagoSemanal': pagoSemanal,
                    'state': 'pago pendiente',
                    'date': current.strftime("%d-%m-%Y %H:%M")
                    }
            newexp = int(session["exp"]) + 150
            gamification(session["level"], newexp)
            card = db.child("users").child(session["localId"]).child("openpay_card").get().val()
            customer = openpay.Customer.retrieve(session["openpay_id"])
            payout = openpay.Payout.create_as_merchant(
                method='card',
                destination_id = card["id"],
                amount = amount, 
                description="Prestamo", 
                order_id=current.strftime("%d-%m-%Y %H:%M")
            )
            updated = {"level": session["level"],
                        "exp": session["exp"],
                        "state": "Adeudo",
                        "debt": total
            }
            db.child("users").child(session["localId"]).set(updated)
            #db.child("users").child(session["localId"]).update({"level": session["level"]})
            #db.child("users").child(session["localId"]).update({"exp": session["exp"]})
            #db.child("users").child(session["localId"]).update({"state": 'Adeudo'})
            db.child("loans").child(session['localId']).push(data)

            return render_template("loan.html", form=form, loanAccepted = "Prestamo realizado de manera correcta")
        except:
            return render_template("loan.html", form=form, message = "Se presento un error al realizar la operacion")
    elif request.method == "GET":
        if "email" in session :
            data = db.child("users").child(session["localId"]).get().val()
            if data['state'] == "Adeudo":
                return redirect(url_for("payment"))
            else:
                return render_template('loan.html', form = form)
        else :
            return redirect(url_for("index"))

@app.route("/payment", methods = ["GET", "POST"])
def payment():
    form = LoanForm()
    if "email" in session:
        if request.method == "POST":
            try:
                current = datetime.datetime.now()
                data = db.child("users").child(session["localId"]).get().val()

                fee = openpay.Fee.create(
                    customer_id = session["openpay_id"],
                    amount = int(data['debt']),
                    description = "Pago de codigo",
                    order_id = "idPago"+current.strftime("%d-%m-%Y %H:%M")
                )
                db.child("users").child(session["localId"]).update({"state": "Regular"})
                #data = db.child("loans").child(session["localId"]).set({"state": "pagado"})
                return render_template("loan.html", form = form, loanAccepted = "Tu pago ha sido recibido exitosamente, pyedes volver a pedir prestamos")
            except openpayError.APIError as e:
                return render_template("payment.html", error_message = "Ocurrio un error al realizar el pago", error_details = "No se han encontrado fondos suficientes en la cuenta en la tarjeta")
        elif request.method == "GET":
            if "email" in session:
                return render_template("payment.html")
            else:
                return redirect(url_for("index"))
    else :
        return redirect(url_for("index"))
        
@app.route("/support")
def support():
    if "email" in session :
        return render_template("support.html")
    else :
        return redirect(url_for("index"))
        
@app.route("/settings", methods = ["GET","POST"])
def settings():
    form = settingsForm()
    
    if "email" in session :
        if request.method =="GET":
            return render_template("settings.html", form = form)
        elif request.method == "POST":
            if form.validate() == False:
                return render_template("settings.html", form = form)
            else:
                customer = openpay.Customer.retrieve(session["openpay_id"])
                card = request.form.get('card')
                cvv = request.form.get('cvv')
                month = request.form.get('month')
                year = request.form.get('year')
                address = request.form.get('address')
                zipcode = request.form.get('zipcode')
                state = request.form.get('state')
                city = request.form.get('city')
                try:
                    card = customer.cards.create(
                        card_number=card,
                        holder_name=session["fname"]+" "+session["lname"],
                        expiration_year= year,
                        expiration_month= month,
                        cvv2=cvv,
                        address={
                            "city": city,
                            "country_code":"MX",
                            "postal_code": zipcode,
                            "line1": address,
                            "state": state
                    })
                    db.child("users").child(session["localId"]).update({"level": 1})
                    session["level"] = 1
                except openpayError.CardError as e:
                    return render_template("settings.html", form = form, not_accepted="Tu tarjeta fue rechazada")
                    
                
                db.child("users").child(session["localId"]).update({"openpay_card": card})
                db.child("users").child(session["localId"]).update({"openpay_card_id": card.id})
                
                return render_template("settings.html", form = form, accepted="Tu tarjeta fue aceptada")
                
    else:
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
