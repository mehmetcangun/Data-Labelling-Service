from flask import current_app, flash, redirect, url_for, render_template, request, abort
from user import get_user

from forms import LoginForm, RegisterForm, DomainsForm, SubdomainsForm, CriteriasForm, ImagesForm

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
  'domains': DomainsForm,
  'subdomains': SubdomainsForm,
  'criterias': CriteriasForm,
  'images': ImagesForm
}

from database import Database

@login_required
@admin_required
def form_operation(name, method, key=None, only_admin=True, FK=None):
  data = None
  message = ""

  if method == 'add':
    data = all_forms[name]()
    data.init_key(key=key, FK=FK, request = request)
    if data.validate_on_submit():
      message, key = data.save()
      if key != -1:
        return redirect(url_for(name+"_details_page", key=key))
  
  elif method == 'update':
    data = all_forms[name]()
    data.init_key(key=key, FK=FK, request = request)
    if data.validate_on_submit():
      message, detectkey = data.save()
      if detectkey != -1:
        return redirect(url_for(name+"_details_page", key=key))
    data.init_data()
  
  elif method == 'delete':
    data = all_forms[name]()
    data.init_key(key=key, FK=FK, request = request)
    if request.method == "POST":
      message, key = data.delete()
      if key != -1:
        flash("domain deleted")
        return redirect(url_for(name+"_index_page"))
  
  
  elif method == 'details':
    domain = Database()
    data = domain.select_query_by_id(key, name, name[:-1]+'_id')

    flash("domain details")
  
  
  elif method == 'index':
    domain = Database()
    data = domain.select_query(name)
    flash("domain index")
  
  
  return render_template(name + "/" + method + ".html", data=data, message=message)

def domains_index_page():
  return form_operation('domains', 'index')

def domains_add_page():
  return form_operation('domains', 'add')

def domains_update_page(key):
  return form_operation('domains', 'update', key=key)

def domains_delete_page(key):
  return form_operation('domains', 'delete', key=key)
  
def domains_details_page(key):
  return form_operation('domains', 'details', key=key)

def subdomains_index_page():
  return form_operation('subdomains', 'index')

def subdomains_add_page(domain_id):
  return form_operation('subdomains', 'add', FK=[('domain_id', domain_id)])

def subdomains_update_page(key):
  return form_operation('subdomains', 'update', key=key)

def subdomains_delete_page(key):
  return form_operation('subdomains', 'delete', key=key)

def subdomains_details_page(key):
  return form_operation('subdomains', 'details', key=key)

def criterias_index_page():
  return form_operation('criterias', 'index')

def criterias_add_page():
  #user_id = current_user.user_id
  user_id = 2
  return form_operation('criterias', 'add', FK=[('user_id', user_id)])

def criterias_update_page(key):
  return form_operation('criterias', 'update', key=key)

def criterias_delete_page(key):
  return form_operation('criterias', 'delete', key=key)

def criterias_details_page(key):
  return form_operation('criterias', 'details', key=key)

def images_index_page():
  return form_operation('images', 'index')

def images_add_page(criteria_id):
  #user_id = current_user.user_id
  user_id = 2
  return form_operation('images', 'add', FK=[('user_id', user_id), ('criteria_id', criteria_id)])

def images_update_page(key):
  return form_operation('images', 'update', key=key, )

def images_delete_page(key):
  return form_operation('images', 'delete', key=key)

def images_details_page(key):
  return form_operation('images', 'details', key=key)