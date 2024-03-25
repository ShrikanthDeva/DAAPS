import os
import glob
from pymongo import MongoClient
from os.path import join, dirname, realpath
from dotenv import load_dotenv
import base64
from datetime import datetime
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
from register import User,LoginForm,user_details,Aadhar_details,FIR

import sys
import numpy
from finger_function.enhance import image_enhance
from skimage.morphology import skeletonize, thin


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

ALLOWED_EXTENSIONS = set(['tif'])


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


class Aadhar_details(db.Model, UserMixin):
    aadhar = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    contact = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.DateTime(),nullable=False)
    f_name = db.Column(db.String(20), nullable=False, unique=True)
    m_name = db.Column(db.String(20), nullable=False, unique=True)

class FIR(db.Model, UserMixin):
    aadhar = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    contact = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.DateTime(),nullable=False)
    informant_name = db.Column(db.String(20), nullable=False)
    informant_relation = db.Column(db.String(20), nullable=False)
    fir_no = db.Column(db.Integer, nullable=False, unique=True)
    fir_date = db.Column(db.DateTime(),nullable=False)
    police = db.Column(db.String(20), nullable=False)


####################3
def removedot(invertThin):
    temp0 = numpy.array(invertThin[:])
    temp0 = numpy.array(temp0)
    temp1 = temp0/255
    temp2 = numpy.array(temp1)
    temp3 = numpy.array(temp2)

    enhanced_img = numpy.array(temp0)
    filter0 = numpy.zeros((10,10))
    W,H = temp0.shape[:2]
    filtersize = 6

    for i in range(W - filtersize):
        for j in range(H - filtersize):
            filter0 = temp1[i:i + filtersize,j:j + filtersize]

            flag = 0
            if sum(filter0[:,0]) == 0:
                flag +=1
            if sum(filter0[:,filtersize - 1]) == 0:
                flag +=1
            if sum(filter0[0,:]) == 0:
                flag +=1
            if sum(filter0[filtersize - 1,:]) == 0:
                flag +=1
            if flag > 3:
                temp2[i:i + filtersize, j:j + filtersize] = numpy.zeros((filtersize, filtersize))
    return temp2


def get_descriptors(img):
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	img = clahe.apply(img)
	img = image_enhance.image_enhance(img)
	img = numpy.array(img, dtype=numpy.uint8)
	# Threshold
	ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
	# Normalize to 0 and 1 range
	img[img == 255] = 1

	#Thinning
	skeleton = skeletonize(img)
	skeleton = numpy.array(skeleton, dtype=numpy.uint8)
	skeleton = removedot(skeleton)
	# Harris corners
	harris_corners = cv2.cornerHarris(img, 3, 3, 0.04)
	harris_normalized = cv2.normalize(harris_corners, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32FC1)
	threshold_harris = 125
	# Extract keypoints
	keypoints = []
	for x in range(0, harris_normalized.shape[0]):
		for y in range(0, harris_normalized.shape[1]):
			if harris_normalized[x][y] > threshold_harris:
				keypoints.append(cv2.KeyPoint(y, x, 1))
	# Define descriptor
	orb = cv2.ORB_create()
	# Compute descriptors
	_, des = orb.compute(img, keypoints)
	return (keypoints, des)


def finger_find():

	test_image = r"C:/Users/shri1/sih/sih-project-2022/sih-project-final/finger_function/database/102_1.tif"
	print(test_image)
	img1 = cv2.imread(test_image, cv2.IMREAD_GRAYSCALE)
	# cv2.imshow("vhvg",img1)
	kp1, des1 = get_descriptors(img1)


	folder_dir = r"C:/Users/shri1/sih/sih-project-2022/sih-project-final/finger_function/fingerprints"
	temp_fingerprints = []
	for images in os.listdir(folder_dir):
    # check if the image ends with tif
		if (images.endswith(".tif")):
			temp_fingerprints.append(images)

	for i in range(len(temp_fingerprints)):

		image_name = r"C:/Users/shri1/sih/sih-project-2022/sih-project-final/finger_function/fingerprints/" + temp_fingerprints[i]
		img2 = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
		kp2, des2 = get_descriptors(img2)

		# Matching between descriptors
		bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
		matches = sorted(bf.match(des1, des2), key= lambda match:match.distance)
		
		# Calculate score
		score = 0
		for match in matches:
			score += match.distance
		score_threshold = 33
		if score/len(matches) < score_threshold:
			person_name = temp_fingerprints[i]
			person_name = person_name.rsplit(".",1)[0]
			print("owner of finger print =",person_name)
			return person_name
			break
	else :
		print("Fingerprint does not match.")


#########################3




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
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join("C:/Users/shri1/sih/sih-project-2022/sih-project-final/finger_function/database/", "fingerprint.tif"))
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
    print("finger")
    NAME = finger_find()
    print(NAME)
    info = Aadhar_details.query.filter_by(name=NAME).first()
    return render_template("details_admin.html", Name=info.name, Contact=info.contact,
                           Address=info.address, data_img="", aadhar=info.aadhar)
     


@app.route("/finger")
def find_finger():
    print("finger")
    global NAME
    NAME = finger_find()
    print(NAME)
    return after_find(NAME)


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
        form = request.form
        dob = str(form["dob"]) 
        new_dob = datetime(int(dob[:4]),int(dob[5:7]),int(dob[8:10]))
        fir_date = str(form["fir_date"])  
        new_fir_date = datetime(int(fir_date[:4]),int(fir_date[5:7]),int(fir_date[8:10]))
        new_user = FIR(name=form["name"],aadhar=form["aadhar"],dob= new_dob,contact=form["contact"],address=form["address"],gender=form["gender"],informant_name=form["informant_name"],informant_relation=form['informant_relation'],fir_no=form["fir_no"],fir_date = new_fir_date,police = form["police"])
        db.session.add(new_user)
        db.session.commit()
        return render_template("admin.html")
       


@app.route("/delete_fir", methods=["GET", "POST"])
@login_required
def delete_fir():
    if request.method == "GET":
        return render_template("delete.html")
    else:
        form = request.form
        print(form["fir_no"])
        fir_det = FIR.query.filter_by(fir_no=int(form['fir_no'])).delete()
        print(fir_det)
        db.session.commit()
        return render_template("admin.html")
        


@app.route("/show_fir")
# @login_required
def show_fir():
    # retrive data from fir_details table
    query = FIR.query.all()
    data = {}
    for i in query:
        data[i.name] = {
            'name' : i.name,
            'aadhar': i.aadhar,
            'dob':i.dob,
            "contact":i.contact,
            "address":i.address,
            "gender":i.gender,
            "informant_name":i.informant_name,
            "informant_relation":i.informant_relation,
            "fir_no":i.fir_no,
            "fir_date":i.fir_date,
            "img":"",
            "police":i.police
        }
    print(data)
    return render_template("show_fir.html", datas=[data])

    # PASS IN DUMMY DATA FOR THE HTML



@app.route("/pending_fir")
# @login_required
def pending_fir():
    # founder_data = pending_found.find({})
    # print(founder_data["Aadhar"])
    
    # create table for recovered
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

# create missing table
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

def after_find(Name):
    print("after_find",Name)
    if Name is None:
        return  render_template("not_found.html") 
    else:
        user = Aadhar_details.query.filter_by(name=NAME).first()
        return render_template("form.html")



if __name__ == "__main__":
    db.create_all(app=app)
    db.session.commit()
    app.run(debug=True, port=3000)
