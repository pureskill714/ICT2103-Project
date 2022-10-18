from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import  LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField, validators
from wtforms.validators import InputRequired, Length, ValidationError, Email

from database.mariadb import MariaDBBackend
from database.models import User

# Setup flask
app = Flask(__name__, static_url_path='/static') # Create an instance of the flask app and put in variable app
app.config['SECRET_KEY'] = 'thisisasecretkey' # Flask uses secret key to secure session cookies and protect our webform

# Setup flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Login failed. Please try again."

# Setup database
db = MariaDBBackend()

# This callback is used by flask login to load the user object from the user id stored in the session
@login_manager.user_loader
def load_user(user_id):
    user = db.getUser(user_id)
    return None if user is None else User.fromTuple(user)

# The form on the login page
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
        userRow = db.getUser(form.username.data)
        if userRow is not None:
            user = User.fromTuple(userRow)
            if user.password == form.password.data:
                login_user(user)
                return render_template('staffdashboard.html')
        flash("Username or Password incorrect. Please try again")
    return render_template('login.html', form=form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required  # ensure is logged then, only then can log out
def logout():
    logout_user()  # log the user out
    return redirect(url_for('login'))  # redirect user back to login page

if __name__ == '__main__':
    app.run(debug=True)
