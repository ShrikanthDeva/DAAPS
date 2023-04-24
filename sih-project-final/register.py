from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,DateField,IntegerField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
# print(app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)


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


class Aadhar_details(db.Model, UserMixin):
    aadhar = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    contact = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.DateTime(),nullable=False)
    f_name = db.Column(db.String(20), nullable=False, unique=True)
    m_name = db.Column(db.String(20), nullable=False, unique=True)

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def home_route():
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
# @login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout', methods=['GET', 'POST'])
# @login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form:  #.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return {'success':  True}
    return {'success':  False}

# delete police admin
def delete_admin(u_id):
    User.query.filter_by(id=u_id).delete()
    db.session.commit()
    print("DELETED",u_id)


class RegisterFormUser(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "name"})

    aadhar = IntegerField(validators=[InputRequired(), Length(min=8, max=8)], render_kw={"placeholder": "aadhar"})

    dob = StringField(validators=[InputRequired()], render_kw={"placeholder": "dob"})
    
    contact = IntegerField(validators=[InputRequired(), Length(min=10, max=10)], render_kw={"placeholder": "contact"})

    address = StringField(validators=[InputRequired(), Length(min=10, max=100)], render_kw={"placeholder": "address"})

    gender = StringField(validators=[InputRequired(), Length(min=8, max=8)], render_kw={"placeholder": "gender"})
 
    f_name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "f_name"})
 
    m_name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "m_name"})


@ app.route('/register_users', methods=['GET', 'POST'])
def register_user():
    form = RegisterFormUser()
    if form:  #.validate_on_submit(): 
        dob = str(form.dob.data)  
        new_dob = datetime(int(dob[:4]),int(dob[5:7]),int(dob[8:10]))
        # print(new_dob)
        new_user = Aadhar_details(name=form.name.data,aadhar=form.aadhar.data,dob=new_dob,contact=form.contact.data,address=form.address.data,gender=form.gender.data,f_name=form.f_name.data,m_name=form.m_name.data)
        db.session.add(new_user)
        db.session.commit()
        return {'success':  True}
    return {'success':  False}



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)


user_details = {
    'ajay kumar':
    {
        'name' : 'Ajay Kumar',
        'contact' :'123456789',
        'address' : 'No: 12 ,nest-wings apartment, Coimbatore ',
        'aadhar' : '987654321'
    },
    'dharnish':
    {
       'name' : 'Dharnish',
        'contact' :'123456789',
        'address' : 'No: 12 ,nest-wings apartment, Coimbatore ',
        'aadhar' : '987654321'
    },
    'asif':
    {
        'name' : 'Asif',
        'contact' :'123456789',
        'address' : 'No: 12 ,nest-wings apartment, Coimbatore ',
        'aadhar' : '987654321'
    },
    'priyanka':
    {
        'name' : 'Priyanka',
        'contact' :'123456789',
        'address' : 'No: 12 ,nest-wings apartment, Coimbatore ',
        'aadhar' : '987654321'
    },
    'shrikanth':
    {
        'name' : 'Shrikanth D',
        'contact' :'123456789',
        'address' : 'No: 12 ,nest-wings apartment, Coimbatore ',
        'aadhar' : '987654321'
    },
    'xyz':
    {
        "name": "XYZ",
        "contact": "98262308621",
        "address":"ABCD EFGH",
        "aadhar": "1234567",
        "fir_no": "S2-780",
        "fir_date": "20-7-2019",
        "gender": "Male",
        "dob": "13-6-1999",
        "img": "",
        "informant_name": "ABC",
        "informant_relation": "Friend",
        "police": "A-102"
    }
}