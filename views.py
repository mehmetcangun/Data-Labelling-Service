from flask import current_app, flash, redirect, url_for, render_template, request, abort
from forms import LoginForm, DomainsForm, SubdomainsForm, CriteriasForm, ImagesForm, LabelsForm, UsersForm

from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from passlib.hash import pbkdf2_sha256 as hasher

from functools import wraps
from database import Database

def home_page():
  return render_template("home.html")

class User(UserMixin):
  def __init__(self, email, password):
    self.email = email
    self.password = password
    self.is_admin = False
  
  def get_id(self):
    return self.email

def login_page():
  form = LoginForm()
  if form.validate_on_submit():
    email = form['email'].data
    print("EMAIL: ", email)
    user = get_user(email)
    if user is not None:
      password = form["password"].data
      if hasher.verify(password, user.password):
        login_user(user)
        next_url = request.args.get('next', url_for("home_page"))
        return redirect(next_url)
      flash("Invalid credentials.")
    flash("Invalid credentials.")
  return render_template("login.html", form=form)

def get_user(user_email):
  db = Database()
  user_ = db.select_query_by_id(user_email, "users", where="email")
  if user_ is not None:
    user = User(user_email, user_['password'])
    user.is_admin = True if user_['usertype'] == 0 else False
    return user
  return None

@login_required
def logout_page():
  logout_user()
  return redirect(url_for("home_page"))

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
  'images': ImagesForm,
  'labels': LabelsForm,
  'users': UsersForm
}

#@login_required
#@admin_required
def form_operation(name, method, key=None, only_admin=True, FK=None, image_id=None):
  data = None
  message = ""
  if method == 'add':
    data = all_forms[name](key=key, FK=FK, request = request)
    if data.validate_on_submit():
      message, key = data.save()
      if key != -1:
        if image_id is None:
          return redirect(url_for(name+"_details_page", key=key))
        return redirect(url_for(name+"_details_page", key=key, image_id=image_id))
  
  elif method == 'update':
    data = all_forms[name](key=key, FK=FK, request = request)
    if data.validate_on_submit():
      message, detectkey = data.save()
      if detectkey != -1:
        if image_id is None:
          return redirect(url_for(name+"_details_page", key=key))
        return redirect(url_for(name+"_details_page", key=key, image_id=image_id))
    data.init_data()
  
  elif method == 'delete':
    data = all_forms[name](key=key, FK=FK, request = request)
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

def labels_index_page(image_id):
  
  query = """select
       lb.label_id as label_id,
       d.name as domain_name,
       sd.name as subdomain_name,
       d.description as domain_description,
       d.color as domain_color,
       d.priority_rate as domain_priority_rate,
       sd.icon as subdomain_icon,
       img.most_contribution,
       img.url_path,
       lb.is_correct
        from
        domains as d inner join subdomains as sd on d.domain_id = sd.subdomain_id inner join
        labels as lb on lb.subdomain_id = sd.subdomain_id inner join
        images as img on img.image_id = lb.image_id;
    """
  
  labels = Database()
  data = labels.select_query(query=query)

  message = "all is done."
  
  return render_template("labels/index.html", image_id = image_id, data=data, message=message)

  #return form_operation('labels', 'index', FK=[('image_id', image_id)])

def labels_add_page(image_id):
  return form_operation('labels', 'add', FK=[('image_id', image_id)])

def labels_update_page(image_id, key):
  return form_operation('labels', 'update', key=key, FK=[('image_id', image_id)], image_id=image_id)

def labels_delete_page(image_id, key):
  return form_operation('labels', 'delete', key=key, FK=[('image_id', image_id)], image_id=image_id)

def labels_details_page(image_id, key):
  return form_operation('labels', 'details', key=key, FK=[('image_id', image_id)], image_id=image_id)


def users_index_page():
  return form_operation('users', 'index')

def users_add_page(usertype):
  return form_operation('users', 'add', FK=[('usertype', usertype-8)])

def users_update_page(key):
  return form_operation('users', 'update', key=key)

def users_delete_page(key):
  return form_operation('users', 'delete', key=key)
  
def users_details_page(key):
  return form_operation('users', 'details', key=key)
