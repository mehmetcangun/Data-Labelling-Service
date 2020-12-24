from flask import current_app, flash, redirect, url_for, render_template, request, abort
from user import get_user

from forms import LoginForm, RegisterForm, DomainForm, SubdomainForm

from flask_login import login_user, logout_user, login_required, current_user
from passlib.hash import pbkdf2_sha256 as hasher

from functools import wraps

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

def register_page():
  form = RegisterForm()
  if form.validate_on_submit():
    flash("sslog out user...")
    return redirect(url_for("home_page"))
  return render_template("register.html", form=form)


def admin_required(f):
  @wraps(f)
  def check_user_type(*args, **kwargs):
    if current_user.is_admin == False:
      return abort(403)
    return f(*args, **kwargs)
  return check_user_type


all_forms = {
  'domains': DomainForm,
  'subdomains': SubdomainForm
}

from database import Database

@login_required
@admin_required
def form_operation(name, method, key=None, only_admin=True, FK=None):
  data = None
  message = ""
  if method == 'add':
    data = all_forms[name]()
    data.init_key(key=key, FK=FK)
    if data.validate_on_submit():
      message, key = data.save()
      if key != -1:
        return redirect(url_for(name+"_details_page", key=key))
  elif method == 'update':
    data = all_forms[name]()
    data.init_key(key=key, FK=FK)
    if data.validate_on_submit():
      message, detectkey = data.save()
      if detectkey != -1:
        return redirect(url_for(name+"_details_page", key=key))
  
  elif method == 'details':
    domain = Database()
    data = domain.select_query_by_id(key, name, name[:-1]+'_id')
    flash("domain details")
  elif method == 'delete':
    if request.method == "POST":
      delete_ = {
        'class_name': 'domains',
        'PK': 'domain_id',
        'data': {
        },
        'where': {
          'domain_id': key
        }
      }
      domain = Database()
      message, key = domain.delete(delete_)
      if key != -1:
        flash("domain deleted")
        return redirect(url_for("home_page"))

  elif method == 'index':
    domain = Database()
    data = domain.select_query(name)
    flash("domain index")
  return render_template(name + "/" + method + ".html", data=data, message=message)

def domain_index_page():
  return form_operation('domains', 'index')

def domain_add_page():
  return form_operation('domains', 'add')

def domain_update_page(key):
  return form_operation('domains', 'update', key=key)

def domain_delete_page(key):
  return form_operation('domains', 'delete', key=key)
  
def domains_details_page(key):
  return form_operation('domains', 'details', key=key)

def subdomain_index_page():
  return form_operation('subdomains', 'index')

def subdomain_add_page(domain_id):
  return form_operation('subdomains', 'add', FK=[('domain_id', domain_id)])

def subdomain_update_page(key):
  return form_operation('subdomains', 'update', key=key)

def subdomain_delete_page(key):
  return form_operation('subdomains', 'delete', key=key)

def subdomains_details_page(key):
  return form_operation('subdomains', 'details', key=key)