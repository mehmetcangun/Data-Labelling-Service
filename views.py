from flask import current_app, flash, redirect, url_for, render_template, request
from user import get_user
from forms import LoginForm
from flask_login import login_user, logout_user, login_required
from passlib.hash import pbkdf2_sha256 as hasher

def home_page():
  return render_template("home.html")

def login_page():
  form = LoginForm()
  if form.validate_on_submit():
    username = form.data["username"]
    user = get_user(username)
    if user is not None:
      password = form.data["password"]
      if hasher.verify(password, user.password):
        login_user(user)
        next_url = request.args.get('next', url_for("home_page"))
        return redirect(next_url)
      flash("Invalid credentials.")
  return render_template("login.html", form=form)

@login_required
def logout_page():
  logout_user()
  flash("log out user...")
  return redirect(url_for("home_page"))
  