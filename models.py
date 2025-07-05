from app import db
from werkzeug.security import generate_password_hash, check_password_hash  
from datetime import datetime
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=True)  
    gender = db.Column(db.String(10), nullable=True)  
    phone_number = db.Column(db.String(15), nullable=True)
    xray_image = db.Column(db.String(200), nullable=True)
    tumor_stage = db.Column(db.String(50), nullable=True)  
    biopsy_file = db.Column(db.String(200), nullable=True)  
    report_pdf = db.Column(db.String(200), nullable=True)  
    brain_mri_image = db.Column(db.String(100), nullable=True)
    brain_mri_class = db.Column(db.String(100), nullable=True)
    brain_mri_confidence = db.Column(db.Float, nullable=True)
    brain_report_pdf = db.Column(db.String(200), nullable=True)
    result = db.Column(db.String(100), nullable=True)

    def __init__(self, username, email, password,age,gender,phone_number):
        self.username = username
        self.email = email
        self.password = password
        self.age = age
        self.gender = gender
        self.phone_number = phone_number


def set_password(self, password):
        self.password = generate_password_hash(password)

def check_password(self, password):
    return check_password_hash(self.password, password)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    def __init__(self, username, email, password, specialization=None, phone=None):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.specialization = specialization
        self.phone = phone


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password) 


