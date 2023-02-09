import os
import glob
from pymongo import MongoClient
from os.path import join, dirname, realpath
from dotenv import load_dotenv
from source.main_video import face
from source.simple_facerec import SimpleFacerec
import base64
import datetime
from flask import Flask, render_template, url_for, redirect, request, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
# from processfinger import finger
import cv2
from werkzeug.utils import secure_filename

import numpy as np



# NAME = None
# client = MongoClient("mongodb://localhost:27017/")
# db = client["adhaar_data"]
# adhar = db["adhaar"]
# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)
# client = MongoClient(os.environ.get("MONGOURL"))
# db = client["aadharDB"]
# aadhar = db["aadhar_data"]
# pending_found = db["pending_found"]
# fir = db["fir_data"]
# found = db["found"]
# finger_data = db["fingerDB"]


# AJAY FACE RECOG CODE
sfr = SimpleFacerec()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET")
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


@app.route("/findPic")
def find_by_pic():
    global NAME
    encode()
    # ajay code
    NAME = face()
    # priyanka find from the localstorage for the aadhar details call the aadhar asif code
    return after_find()



@app.route("/admin_find")
# @login_required
def admin_find():
    return render_template("admin_find.html")

@app.route('/admin_find', methods=['POST'])
# @login_required
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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], "fingerprint.bmp"))
        # print('upload_image filename: ' + filename)
        return redirect("/admin_finger_find")
    else:
        flash('Allowed image types are - bmp')
        return redirect(request.url)


@app.route("/admin_pic_find")
# @login_required
def admin_pic_find():
    name = face()
    encode()
    aadhar_info = aadhar.find_one({"aadhar": name})
    return render_template("details_admin.html", Name=aadhar_info["name"], Contact=aadhar_info["Contact"],
                           Address=aadhar_info["Address"], data_img=aadhar_info["img"].decode("UTF-8"), aadhar=name)
    
    # call ajay function for camera recog




@app.route("/admin_finger_find")
# @login_required
def admin_finger_find():
    name = finger()
    aadhar_info = aadhar.find_one({"aadhar": name})
    return render_template("details_admin.html", Name=aadhar_info["name"], Contact=aadhar_info["Contact"],
                           Address=aadhar_info["Address"], data_img=aadhar_info["img"].decode("UTF-8"))

    # call ajay function for fingerprint 


@app.route("/finger")
def find_finger():
    print("finger")
    global NAME
    NAME = finger()
    print(NAME)
    return after_find()

    # call ajay function for fingerprint



@app.route("/found_form", methods=['POST'])
def found_form():
    global NAME
    local_name = NAME
    NAME = None
    # print(f"ypo{NAME}")
    # print(f"ypo{local_name}")
    data = request.form
    # print(data)
    aadhar_info = fir.find_one({"Aadhar": local_name})
    doc = {
        "founder_name": data["name"],
        "founder_contact": data["contact"],
        "address_found": data["address"],
        "date_found": datetime.date.today().strftime("%d-%B-%Y"),
        "Aadhar": local_name,
        "name": aadhar_info["name"],
        "Contact": aadhar_info["Contact"],
        "img": aadhar_info["img"]
    }
    # print(doc)
    pending_found.insert_one(doc)
    return render_template("details.html", Name=aadhar_info["name"], Contact=aadhar_info["Contact"], police=aadhar_info["police"], Address=aadhar_info["Address"], data_img=aadhar_info["img"], info_name=aadhar_info["informant_name"], info_relation=aadhar_info["informant_relation"])


@app.route("/admin")
# @login_required
def admin():
    return render_template("admin.html")



# def encode():
#     add_local()
#     sfr.add_data()
#     del_local()


@app.route("/register_fir", methods=["GET", "POST"])
# @login_required
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
            "img": aadhar.find_one({"aadhar": data["aadhar"]})["img"].decode("UTF-8"),
            "informant_name": data["informant_name"],
            "informant_relation": data["informant_relation"],
            "police": data["police"]
        }
        # fir.insert_one(doc)
        # return redirect(url_for("show_fir"))
        print(doc)
        return


@app.route("/delete_fir", methods=["GET", "POST"])
# @login_required
def delete_fir():
    if request.method == "GET":
        return render_template("delete.html")
    else:
        data = request.form
        print(data)
        return
        # found_data = fir.find_one_and_delete({"Aadhar": data["aadhar"], "fir_no": data["fir_no"]})
        # doc = {
        #     "name": found_data["name"],
        #     "img": found_data["img"],
        #     "date": datetime.date.today().strftime("%d-%B-%Y"),
        #     "gender": found_data["gender"]
        # }
        # found.insert_one(doc)
        # return redirect(url_for("show_fir"))
        


@app.route("/show_fir")
# @login_required
def show_fir():
    data = fir.find({})
    return render_template("show_fir.html", datas=data)

    # PASS IN DUMMY DATA FOR THE HTML



@app.route("/pending_fir")
# @login_required
def pending_fir():
    founder_data = pending_found.find({})
    # print(founder_data["Aadhar"])
    return render_template("recovered_details.html", data=founder_data)

   # PASS IN DUMMY DATA FOR THE HTML


@app.route("/recovered", defaults={"filter": "all"})
@app.route("/recovered/<filter>")
def recovered(filter):
    data = None
    if filter == "female":
        data = found.find({"gender": "female"})
    elif filter == "male":
        data = found.find({"gender": "male"})
    else:
        data = found.find({})
    return render_template("found.html", datas=data, raj=filter)

    # PASS IN DUMMY DATA FOR THE HTML


@app.route("/missing", defaults={"filter": "all"})
@app.route("/missing/<filter>")
def missing(filter):
    data = None
    if filter == "female":
        data = fir.find({"gender": "female"})
    elif filter == "male":
        data = fir.find({"gender": "male"})
    else:
        data = fir.find({})
    return render_template("missing.html", datas=data, raj=filter)
    
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


def add_local():
    data = aadhar.find({"is_encoded": "false"})
    for user in data:
        decodeit = open(f'source/images/{user["aadhar"]}.jpeg', 'wb')
        decodeit.write(base64.b64decode(user["img"]))
        decodeit.close()

    # with open("1234.jpg", "rb") as image2string:
    #     converted_string = base64.b64encode(image2string.read())
    # print(converted_string)
    # yo = {
    #     "img": converted_string,
    #     "name": "raj"
    # }
    # user_img.insert_one(yo)


def del_local():
    aadhar.update_many(filter={"is_encoded": "false"}, update={"$set": {"is_encoded": "true"}})
    images_path = glob.glob(os.path.join("source/images", "*.*"))
    for img in images_path:
        print(img)
        os.remove(img)
    # os.remove("source/images")


# ADD THE FINGER SCRIPTS
def finger():
    sample = cv2.imread("C:/Users/shri1/sih/sih-project-2022/sih-project-final/static/fingerprint.bmp")

    best_score = 0
    filename = None
    image = None
    kp1, kp2, mp = None, None, None
    i = 0
    # client = MongoClient("mongodb+srv://kartik:aadhar_data@cluster0.6nbl1l4.mongodb.net/?retryWrites=true&w=majority")
    # db = client["aadharDB"]
    # finger_data = db["fingerDB"]
    files = finger_data.find({})
    for file in files:
        print(i)
        i=i+1
        fingerimg = np.uint8(np.array(file["finger"]))
        # print(fingerimg.dtype)
        # print(sample.dtype)
        fingerprint_image=cv2.cvtColor(fingerimg, cv2.COLOR_BGR2GRAY)
        # print(sample)
        sift = cv2.SIFT_create()

        keypoints_1, descriptors_1 = sift.detectAndCompute(sample, None)
        keypoints_2, descriptors_2 = sift.detectAndCompute(fingerprint_image, None)

        matches = cv2.FlannBasedMatcher({'algorithm': 1, 'trees': 10},
                                        {}).knnMatch(descriptors_1, descriptors_2, k=2)

        match_points = []

        for p, q in matches:
            if p.distance < 0.1 * q.distance:
                match_points.append(p)

        keypoints = 0
        if len(keypoints_1) < len(keypoints_2):
            keypoints = len(keypoints_1)
        else:
            keypoints = len(keypoints_2)
        # print("raj")
        if len(match_points) / keypoints * 100 > best_score:
            # print("if")
            best_score = len(match_points) / keypoints * 100
            filename = file["Aadhar"]
            image = fingerprint_image
            kp1, kp2, mp = keypoints_1, keypoints_2, match_points
        # break

    print(f"BEST MATCH:   {filename}")
    print("SCORE: " + str(best_score))

    # result = cv2.drawMatches(sample, kp1, image, kp2, mp, None)
    # result = cv2.resize(result, None, fx=1, fy=1)
    # cv2.imshow("Result", result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return filename

# ASIF HTML FILE FOR NOT FOUND
def after_find():
    global NAME
    aadhar_info = aadhar.find_one({"aadhar": NAME})
    if aadhar_info is None:
        return "<h1>Aadhar not found</h1>"
    fir_info = fir.find_one({"Aadhar": aadhar_info["aadhar"]})
    if fir_info is None:
        NAME = None
        return render_template("fir.html")
    else:
        return render_template("form.html")



if __name__ == "__main__":
    db.create_all(app=app)
    app.run(debug=True, port=3000)
