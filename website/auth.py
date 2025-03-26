from flask import Blueprint, render_template, redirect, flash, url_for, request
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET','POST'])
def signin():
    if request.method == 'POST':

        email=request.form.get("email")
        password=request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password!', category='error')
        else:
            flash('User doesnot exists!', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email=request.form.get("email")
        #generate username
        preficnum = random.randint(1,9999999)
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username= firstname+lastname+str(preficnum)
        password1=request.form.get("password1")
        password2=request.form.get("password2")
        print(str(email))
        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        if email_exists:
            flash('Email is already in use', category='error')
        elif username_exists:
            flash('Username is already in use', category='error')
        elif password1 != password2:
            flash('Password do not match', category='error')
        elif len(username) < 2:
            flash('Username is too short', category='error')
        elif len(password1) < 6:
            flash('Password is too short', category = 'error')
        elif len(email) < 4:
            flash('Invalid email',  category = 'error')
        else:
            new_user = User(email=email,firstname=firstname, lastname=lastname, username=username,profilepicname='defaultprofilepicname.png',
            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))
    return render_template("signup.html", user=current_user)


@auth.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect(url_for("views.home"))
