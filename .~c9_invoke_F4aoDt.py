from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class SignupForm(FlaskForm):
    first_name = StringField('First name', validators = [DataRequired("Ingresa tu primer nombre")])
    last_name = StringField('Last name', validators = [DataRequired("Ingresa tu apellido")])
    email = StringField('Email', validators = [DataRequired("Ingresa tu correo"), Email("Ingresa tu correo cor")])
    password = PasswordField('Password', validators = [DataRequired("Ingresa la contraseña"), Length(min=6, message="La contraseña tiene que ser de mínimo 6 caracteres")])
    submit = SubmitField('Sign up')
    
    