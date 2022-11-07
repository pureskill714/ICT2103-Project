from datetime import datetime
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, Length

from database.mariadb import MariaDBBackend
from database.firebase import FirebaseBackend
from database.models import BloodDonation, DashboardData, Donor

# Setup flask
app = Flask(__name__) # Create an instance of the flask app and put in variable app
app.config['SECRET_KEY'] = 'thisisasecretkey' # Flask uses secret key to secure session cookies and protect our webform

# Setup flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = ''

# Setup database (only use one of them)
db = MariaDBBackend()
#db = FirebaseBackend()

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
    data = db.getDashboardStats(current_user.branchId)
    return render_template('dashboard_staff.html', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()

    if request.method == 'POST':
        user = db.login(form.username.data, form.password.data)
        if user is not None:
            url = request.args.get('next')
            login_user(user)
            return redirect(url or url_for('home'))
        else:
            flash("Username or password incorrect.")

    return render_template('login.html', form=form)

@app.route('/donors', methods= ['GET', 'POST'])
@login_required
def donors():
    if request.method == 'POST':
        nric = request.form.get('nric')
        name = request.form.get('name')
        dateOfBirth = request.form.get('dateOfBirth')
        contactNo = request.form.get('contactNo')
        bloodType = request.form.get('bloodType')
        donor = Donor(nric, name, dateOfBirth, contactNo, bloodType, None)

        # Depending on the query string do the respective action
        try:
            action = request.args.get('action')
            if action is None or action == 'create':
                # /donor?action=create
                donor.registrationDate = datetime.now()
                db.insertDonor(donor)
            elif action == 'update':
                # /donor?action=update
                db.updateDonor(donor)
            elif action == 'delete':
                # /donor?action=delete
                db.deleteDonorByNRIC(nric)
            db.commit()
            return jsonify(success=True, data=donor.serialize())
        except Exception as e:
            return jsonify(success=False)

    
    donors = db.getAllDonors()
    return render_template('donors.html', donors = donors, today=datetime.now())

@app.route('/donations', methods= ['GET', 'POST'])
@login_required
def donations():
    if request.method == 'POST':
        id = request.form.get('id')
        nric = request.form.get('nric')
        quantity = request.form.get('quantity')
        branchId = request.form.get('branchId')
        donation = BloodDonation(id, nric, quantity, None, branchId, current_user.id, None)

        # Depending on the query string do the respective action
        try:
            action = request.args.get('action')
            if action is None or action == 'create':
                # /donations?action=create
                donation.date = datetime.now()
                donation.id = db.insertDonation(donation)
            elif action == 'delete':
                # /donations?action=delete
                # To implement
                pass
            db.commit()
            return jsonify(success=True, data=donation.serialize())
        except Exception as e:
            return jsonify(success=False)

    donors = db.getAllDonors()
    donations = db.getAllDonations()
    branches = db.getAllBranches()
    return render_template('donations.html', donors = donors, donations = donations, branches = branches)

@app.route('/requests')
@login_required
def requests():
    requests = db.getAllRequests()
    pending = filter(lambda r: not r.fulfilled, requests)
    complete = filter(lambda r: r.fulfilled, requests)
    return render_template('requests.html', pending = pending, complete = complete)

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

@app.route('/query')
@login_required
def query():
    '''Endpoint for AJAX query calls'''
    type = request.args.get('type')
    key = request.args.get('key')
    val = request.args.get('val')

    if type == 'donor':
        if key == 'nric':
            donor = db.getDonorByNRIC(val)
            return jsonify(success=True, data=donor.serialize())

    elif type == 'donation':
        if key == 'bloodType':
            donations = db.getAvailableDonationsByBloodType(val)
            return jsonify(success=True, data=[d.serialize() for d in donations])

    elif type == 'request':
        if key == 'id':
            req = db.getRequestById(val)
            return jsonify(success=True, data=req.serialize())

    return jsonify(success=False, error='Bad query')

if __name__ == '__main__':
    app.run(debug=True)
