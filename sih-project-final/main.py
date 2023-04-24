import os
import glob
from pymongo import MongoClient
from os.path import join, dirname, realpath
from dotenv import load_dotenv
import base64
import datetime
from flask import Flask, render_template, url_for, redirect, request, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from PIL import Image
# from processfinger import finger
import cv2
from werkzeug.utils import secure_filename
import numpy as np
from face_function import face_recognize
from register import user_details,Aadhar_details
from finger_function import fingerprint_test

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/..')


app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['bmp'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
global NAME
NAME = None
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('admin'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_route'))


@app.route("/")
def home_route():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], "fingerprint.bmp"))
        # print('upload_image filename: ' + filename)
        return redirect("/finger")
    else:
        flash('Allowed image types are - bmp')
        return redirect(request.url)

def modify(s):
    return s[0].upper() + s[1:].lower()

@app.route("/findPic")
def find_by_pic():
    global NAME
    # code
    NAME = face_recognize.find_person_name()
    NAME = modify(NAME)
    print(NAME)
    return after_find(NAME)


@app.route("/admin_find")
@login_required
def admin_find():
    return render_template("admin_find.html")

@app.route('/admin_find', methods=['POST'])
@login_required
def upload_admin_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(filename)
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], "fingerprint.bmp"))
        # print('upload_image filename: ' + filename)
        return redirect("/admin_finger_find")
    else:
        flash('Allowed image types are - bmp')
        return redirect(request.url)


@app.route("/admin_pic_find")
@login_required
def admin_pic_find():
    # code
    name = face_recognize.find_person_name()
    name = modify(name)
    info = Aadhar_details.query.filter_by(name=name).first()
    return render_template("details_admin.html", Name=info.name, Contact=info.contact,
                           Address=info.address, data_img="", aadhar=info.aadhar)



@app.route("/admin_finger_find")
@login_required
def admin_finger_find(): 
    # call ajay function for fingerprint
    name = fingerprint_test.finger_find()
    print(name)
    info = Aadhar_details.query.filter_by(name=name).first()
    return render_template("details_admin.html", Name=info.name, Contact=info.contact,
                           Address=info.address, data_img="", aadhar=info.aadhar)
     


@app.route("/finger")
def find_finger():
    print("finger")
    global NAME
    # Name = fingerprint_test.finger_find()
    Name = 'Shrikanth'
    print(Name)
    # user = Aadhar_details.query.filter_by(name=NAME).first()
    # print(user.name)
    return after_find(None)


@app.route("/found_form", methods=['POST'])
def found_form():
    global NAME
    data = request.form
    info = Aadhar_details.query.filter_by(name=NAME).first()
    return render_template("details_admin.html", Name=info.name, Contact=info.contact,
                           Address=info.address, data_img="", aadhar=info.aadhar)


@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")

@app.route("/register_fir", methods=["GET", "POST"])
@login_required
def register_fir():
    if request.method == "GET":
        return render_template("dashboard.html")
    else:
        data = request.form
        # print(data)
        doc = {
            "name": data["name"],
            "Contact": data["contact"],
            "Address": data["address"],
            "Aadhar": data["aadhar"],
            "fir_no": data["fir_no"],
            "fir_date": data["fir_date"],
            "gender": data["gender"],
            "dob": data["dob"],
            "img": "",
            "informant_name": data["informant_name"],
            "informant_relation": data["informant_relation"],
            "police": data["police"]
        }
        print(doc)
        return redirect(request.url)
       


@app.route("/delete_fir", methods=["GET", "POST"])
@login_required
def delete_fir():
    if request.method == "GET":
        return render_template("delete.html")
    else:
        data = request.form
        print(data)
        return redirect(request.url)
        


@app.route("/show_fir")
# @login_required
def show_fir():
    # create dummy data for FIR
    data = user_details['xyz']
    print(data)
    doc = {
            "name": data["name"],
            "Contact": data["contact"],
            "Address": data["address"],
            "Aadhar": data["aadhar"],
            "fir_no": data["fir_no"],
            "fir_date": data["fir_date"],
            "gender": data["gender"],
            "dob": data["dob"],
            "img": "",
            "informant_name": data["informant_name"],
            "informant_relation": data["informant_relation"],
            "police": data["police"]
        }
    return render_template("show_fir.html", datas=[data])

    # PASS IN DUMMY DATA FOR THE HTML



@app.route("/pending_fir")
# @login_required
def pending_fir():
    # founder_data = pending_found.find({})
    # print(founder_data["Aadhar"])
    
    # create dummy data for recovered
    founder_data = {
        "founder_name":'abcd',
        "date_found" : "12-09-2020",
        "address_found":'qwertyuiop',
        "founder_contact":'123456789',
        "name":"xyz",
        "Aadhar":'8765q1313',
        "Contact":"763187191"
    }
    return render_template("recovered_details.html", data=[founder_data])

   # PASS IN DUMMY DATA FOR THE HTML


@app.route("/recovered", defaults={"filter": "all"})
@app.route("/recovered/<filter>")
def recovered(filter):
    data = {
        "name" : "XYZZ",
        "date":"12-2-2-2012"
    }
    # if filter == "female":
    #     data = found.find({"gender": "female"})
    # elif filter == "male":
    #     data = found.find({"gender": "male"})
    # else:
    #     data = found.find({})

    # dummy data
    return render_template("found.html", datas=[data], raj=filter)

    # PASS IN DUMMY DATA FOR THE HTML


@app.route("/missing", defaults={"filter": "all"})
@app.route("/missing/<filter>")
def missing(filter):
    data = {
        "name" : "XYZZ",
        "dob":"12-2-2-2012"
    }
    # if filter == "female":
    #     data = fir.find({"gender": "female"})
    # elif filter == "male":
    #     data = fir.find({"gender": "male"})
    # else:
    #     data = fir.find({})
    return render_template("missing.html", datas=[data], raj=filter)
    
    # PASS IN DUMMY DATA FOR THE HTML



@app.route("/charts")
def chart():
    fir_date = datetime.date.today().strftime("%Y-%m-%d")
    found_date = datetime.date.today().strftime("%d-%B-%Y")
    fir_cnt_male = 8858
    fir_cnt_female = 4763
    found_cnt_male = 1245
    found_cnt_female = 689
    return render_template("charts.html", fir_cnt_female=fir_cnt_female, fir_cnt_male=fir_cnt_male, found_cnt_female=found_cnt_female, found_cnt_male=found_cnt_male)

@app.route("/not_found")
def not_found():
    return render_template("not_found.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/feedback")
def feedback():
    return render_template("feedback.html")


@app.route("/law")
def law():
    return render_template("law.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/miss_pic")
def miss_pic():
    return render_template("photo1.html")

def after_find(NAME):
    if NAME is None:
        return  render_template("not_found.html") 
    else:
        return render_template("form.html")



if __name__ == "__main__":
    db.create_all(app=app)
    db.session.commit()
    app.run(debug=True, port=3000)
