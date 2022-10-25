from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, Length

from database.mariadb import MariaDBBackend
from database.models import BloodDonation, DashboardData, Donor

# Setup flask
app = Flask(__name__) # Create an instance of the flask app and put in variable app
app.config['SECRET_KEY'] = 'thisisasecretkey' # Flask uses secret key to secure session cookies and protect our webform

# Setup flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = ''

# Setup database
db = MariaDBBackend()

# This callback is used by flask login to load the user object from the user id stored in the session
@login_manager.user_loader
def load_user(user_id):
    return db.getUserById(user_id)

# The form on the login page
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),
                                       Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(),
                                         Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")

@app.route('/')
@login_required
def home():
    donorCount, availBlood, requests = db.getDashboardStats()
    data = DashboardData(donorCount, availBlood, requests, {
        'A+': availBlood / 2,
        'A-': availBlood / 4,
        'B+': availBlood / 4,
        'B-': availBlood / 16,
        'AB+': availBlood / 8,
        'AB-': availBlood / 8,
        'O+': availBlood / 16,
        'O-': availBlood / 32
    })
    return render_template('dashboard_staff.html', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        user = db.getUserByUsername(form.username.data)
        if user is not None and user.password == form.password.data:
            url = request.args.get('next')
            login_user(user)
            return redirect(url or url_for('home'))
        else:
            flash("Username or Password incorrect. Please try again")
    return render_template('login.html', form=form)

@app.route('/donors', methods= ['GET', 'POST'])
@login_required
def donors():
    if request.method == 'POST':
        nric =  request.form.get('nric')
        name =  request.form.get('name')
        dateOfBirth =  request.form.get('dateOfBirth')
        contactNo =  request.form.get('contactNo')
        bloodType =  request.form.get('bloodType')
        bloodTypeId = db.getBloodTypeId(bloodType)
        newDonor = Donor(nric, name, dateOfBirth, contactNo, bloodTypeId, datetime.now())
        db.insertDonor(newDonor)
        db.commit()
    
    donors = db.getAllDonors()
    return render_template('donors.html', donors = donors, today=datetime.now())

@app.route('/donations', methods= ['GET', 'POST'])
@login_required
def donations():
    if request.method == 'POST':
        nric =  request.form.get('donorNRIC')
        quantity =  request.form.get('quantity')
        branchId =  request.form.get('branchId')
        newDonation = BloodDonation(None, nric, quantity, datetime.now(), branchId, current_user.id)
        db.insertDonation(newDonation)
        db.commit()

    donors = db.getAllDonors()
    donations = db.getAllBloodDonations()
    branches = db.getAllBranches()
    return render_template('donations.html', donors = donors, donations = donations, branches = branches)

@app.route('/requests')
@login_required
def requests():
    requests = db.getAllBloodRequests()
    return render_template('requests.html', requests = requests)

@app.route('/branches')
@login_required
def branches():
    branches = db.getAllBranches()
    return render_template('branches.html', branches = branches)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()  # log the user out
    flash('Logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
