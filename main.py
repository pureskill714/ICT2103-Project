# Allow users to pass variables into our view function and then dynamically change what we have on our view page
# Dynamically pass variables into the URL
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy  # to create db and an instance of sql Alchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import ForeignKey, DateTime
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, validators
from wtforms.validators import InputRequired, Length, ValidationError, Email
from datetime import date

app = Flask(__name__, static_url_path='/static')  # Create an instance of the flask app and put in variable app
app.config['SECRET_KEY'] = 'thisisasecretkey'  # flask uses secret key to secure session cookies and protect our webform
# against attacks such as Cross site request forgery (CSRF)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Handling the login validation for Staff
login_manager = LoginManager()  # Allow our app and flask login to work together
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = u"Username or Password incorrect. Please try again"


# This user loaded callback is used to reload the user object from the user id stored in the session
@login_manager.user_loader
def load_user_staff(user_id):
    return Staff.query.get(user_id)


# a class as a model. The model will represent the data that will be stored in the database
# this class needs to inherit from db.Model
class Staff(db.Model, UserMixin):  # UserMixin is for validating users
    __tablename__ = 'Staff'
    id = db.Column(db.Integer, primary_key=True)  # This will be primary key
    username = db.Column(db.String(30), nullable=False, unique=True)  # username field is unique
    password = db.Column(db.String(80), nullable=False)  # password field


class Donor(db.Model):
    __tablename__ = 'Donor'
    nric = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    dob = db.Column(db.String(30), nullable=False)
    bloodtype = db.Column(db.String(4), nullable=False)
    contactno = db.Column(db.Integer(), nullable=False)
    registerdate = db.Column(db.String(30), nullable=False)
    registeredby = db.Column(db.String(30), ForeignKey("Staff.id"), nullable=True)


# This form is used to make the fields on the login html page
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),
                                       Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(),
                                         Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    nric = StringField(validators=[InputRequired(),
                                   Length(min=4, max=20)])

    name = StringField(validators=[InputRequired(),
                                   Length(min=4, max=20)])

    dateofbirth = DateField(validators=[InputRequired()])

    bloodtype = StringField(validators=[InputRequired(),
                                        Length(min=1, max=3)])

    contact = IntegerField(validators=[InputRequired()])

    submit = SubmitField("Register")  # Register button once they are done


# App routes help to redirect to different pages of the website
@app.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # check if the user exists in the database
    if form.validate_on_submit():
        staff = Staff.query.filter_by(username=form.username.data).first()
        # If they are in the database,check for their password hashed,compare with real password. If it matches,
        # then redirect them to dashboard page
        if staff:
            login_user(staff)
            return render_template('staffdashboard.html')
        else:
            flash("Username or Password incorrect. Please try again")
    return render_template('login.html', form=form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required  # ensure is logged then, only then can log out
def logout():
    logout_user()  # log the user out
    return redirect(url_for('login'))  # redirect user back to login page


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    today = date.today()
    todaydate_string = today.strftime("%m/%d/%y")
    if form.validate_on_submit():
        dob_string = date.isoformat(form.dateofbirth.data)  # change from DateTime to String
        new_donor = Donor(nric=form.nric.data, name=form.name.data,
                          dob=dob_string, bloodtype=form.bloodtype.data,
                          contactno=form.contact.data, registerdate=todaydate_string)
        db.session.add(new_donor)
        db.session.commit()
        return render_template('staffdashboard.html')

    # if account creation is successful, go to login page, else flash message to user
    if request.method == 'POST':
        if form.validate():
            return render_template('staffdashboard.html')
        else:
            # Check if username already exists in database and return error message
            existing_nric = Donor.query.filter_by(nric=form.nric.data).first()
            if existing_nric:
                flash("This NRIC already exists in the system")

    return render_template('register.html', form=form)


@app.route("/staffdashboard", methods=['GET', 'POST'])
@login_required  # ensure is logged then, only then can access the dashboard
def staffdashboard():
    return render_template('staffdashboard.html')


@app.route('/registersuccess')
@login_required  # ensure is logged then, only then can access the dashboard
def registersuccess():
    return render_template('registersuccess.html')


@app.route('/donortable')
def donortable():
    donors = Donor.query.all()
    return render_template('donortable.html', donors=donors)


@app.route('/donorupdatesearch', methods=['GET', 'POST'])
def donorUpdateSearch():
    return render_template('donorCRUD/donor_update_search.html')


@app.route('/donorupdatevalue', methods=['GET', 'POST'])
def donorUpdateValue():
    nric_no = request.form['nric_no']
    donor = Donor.query.filter_by(nric=nric_no).first()
    if donor:
        return render_template('donorCRUD/donor_update_value.html', donor=donor)
    else:
        return f"Donor with NRIC = {nric_no} Does not exist"


@app.route('/donorupdatesubmit/<string:nric_no>', methods=['GET', 'POST'])
def donorUpdateSubmit(nric_no):
    donor = Donor.query.filter_by(nric=nric_no).first()
    if request.method == 'POST':
        donor.dob = request.form['dob']
        donor.bloodtype = request.form['bloodtype']
        donor.contactno = request.form['contact']
        db.session.commit()
        return render_template('donorCRUD/donor_update_sucess.html')
    else:
        return "failed to update"

@app.route('/donordeletesearch', methods=['GET', 'POST'])
def donorDeleteSearch():
    return render_template('donorCRUD/donor_delete_search.html')

@app.route('/donordeletesubmit', methods=['GET', 'POST'])
def donorDeleteSubmit():
    nric_no_delete = request.form['nric_no_delete']
    donor = Donor.query.filter_by(nric=nric_no_delete).first()
    if request.method == 'POST':
        if donor:
            db.session.delete(donor)
            db.session.commit()
            return render_template('donorCRUD/donor_delete_sucess.html')
        else:
            return f"Donor with NRIC = {nric_no_delete} Does not exist"

if __name__ == '__main__':
    app.run(debug=True)
