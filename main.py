# Allow users to pass variables into our view function and then dynamically change what we have on our view page
# Dynamically pass variables into the URL
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy  # to create db and an instance of sql Alchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField, validators
from wtforms.validators import InputRequired, Length, ValidationError, Email

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


# This form is used to make the fields on the login html page
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),
                                       Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(),
                                         Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")


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


if __name__ == '__main__':
    app.run(debug=True)
