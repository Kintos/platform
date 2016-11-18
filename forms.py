from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class SignupForm(FlaskForm):
    first_name = StringField('First name', validators = [DataRequired("Ingresa tu primer nombre")])
    last_name = StringField('Last name', validators = [DataRequired("Ingresa tu apellido")])
    email = StringField('Email', validators = [DataRequired("Ingresa tu correo"), Email("Ingresa tu correo correcto")])
    phone = StringField('Phone', validators = [DataRequired("Ingresa tu número de celular"), Length(min=10, message="El teléfono tiene que tener al menos 10 digitos")])
    password = PasswordField('Password', validators = [DataRequired("Ingresa la contraseña"), Length(min=6, message="La contraseña tiene que ser de mínimo 6 caracteres")])
    submit = SubmitField('Registrarme')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired("Ingresa tu correo"), Email("Ingresa tu correo correcto")])
    password = PasswordField("Password", validators=[DataRequired("Ingresa la contraseña")])
    submit = SubmitField("Entrar")

class InvestForm(FlaskForm):
    amount = StringField('Amount')
    duration = StringField('Duration')
    total = StringField('Total')
    submit = SubmitField('Invertir ahora')
    
class LoanForm(FlaskForm):
    amount = StringField('Amount')
    duration = StringField('Duration')
    total = StringField('Total')
    submit = SubmitField('Solicitar ahora')
    
class RecoverForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired("Ingresa tu correo"), Email("Ingresa tu correo correcto")])
    submit = SubmitField("Recuperar contraseña")

class settingsForm(FlaskForm):
    card = StringField('card', validators = [DataRequired("Ingresa el numero de tarjeta"), Length(min=16, message="Tu tarjeta debe tener al menos 16 digitos")])
    cvv = StringField('cvv', validators = [DataRequired("Ingresa el código CVV")])
    month = StringField('month', validators = [DataRequired("Ingresa el mes de vencimiento")])
    year = StringField('year', validators = [DataRequired("Ingresa el año de vencimiento")])
    address = StringField('address', validators = [DataRequired("Ingresa tu direccion (Calle y número)")])
    zipcode = StringField('zipcode', validators = [DataRequired("Ingresa tu código postal")])
    state = StringField('state', validators = [DataRequired("Ingresa tu estado")])
    city = StringField('city', validators = [DataRequired("Ingresa tu ciudad")])
    submit = SubmitField("Actualizar")