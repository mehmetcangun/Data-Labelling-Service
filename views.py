from flask import current_app, flash, redirect, url_for, render_template, request, abort
from forms import LoginForm, UsersEdit, ChangePasswordForm, DomainsForm, SubdomainsForm, CriteriasForm, ImagesForm, LabelsForm, UsersForm

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
    self.uid = None
  
  def get_id(self):
    return self.email
  
  def get_uid(self):
    return self.uid

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
        db_ = Database()
        data = {
          'primary_key': 'user_id',
          'table_name': 'users',
          'data': {
            'last_seen': 'NOW()'
          },
          'where': {
            'email': form['email'].data
          }
        }
        db_.update(data)
        next_url = request.args.get('next', url_for("home_page"))
        return redirect(next_url)
      flash("Invalid credentials.")
    flash("Invalid credentials.")
  return render_template("login.html", data=form)

def get_user(user_email):
  db = Database()
  user_ = db.select_query_by_id(user_email, "users", where="email")
  if user_ is not None:
    user = User(user_email, user_['password'])
    user.is_admin = True if user_['usertype'] == 0 else False
    user.uid = user_['user_id']
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

sort_by = {
  'users': {
    'default': 'Default',
    'points_asc': 'Points First Lower',
    'points_desc': 'Points First Higher', 
    'contribution_size_asc': 'Contribution Size Lower', 
    'contribution_size_desc': 'Contribution Size Higher', 
    'join_date_asc': 'Join Date(New)',   
    'join_date_desc': 'Join Date(Old)',  
    'last_seen_asc': 'Last Seen(New)',   
    'last_seen_desc': 'Last Seen(Old)',  
    'uname_asc': 'Name(A-Z)',       
    'uname_desc': 'Name(Z-A)',      
    'surname_asc': 'Surname(A-Z)',     
    'surname_desc': 'Surname(Z-A)'
  },
  'domains': {
    'default': 'Default',
    'domain_name_asc':'Domain Name(A-Z)',
    'domain_name_desc':'Domain Name(Z-A)',
    'domain_priority_rate_asc':'Priority Rate(1-10)',
    'domain_priority_rate_desc':'Priority Rate(10-1)',
    'subdomain_length_asc':'Lower Subdomain Length',
    'subdomain_length_desc':'Greater Subdomain Length'
  },
  'subdomains': {
    'default': 'Default',
    'domain_name_asc':'Domain Name(A-Z)',
    'domain_name_desc':'Domain Name(Z-A)',
    'subdomain_name_asc':'Subdomain Name(A-Z)',
    'subdomain_name_desc':'Subdomain Name(Z-A)',
    'subdomain_priority_rate_asc':'Priority Rate(1-10)',
    'subdomain_priority_rate_desc':'Priority Rate(10-1)',
    'count_images_used_asc':'Count of images used | Increasing',
    'count_images_used_desc':'Count of images used | Decreasing'
  },
  'images':{
    'default': 'Default',
    'user_contribution_asc': 'Total Contribution | Increasing',
    'user_contribution_desc': 'Total Contribution | Decreasing',
    'most_contribution_asc': 'Most Contribution | Increasing',
    'most_contribution_desc': 'Most Contribution | Decreasing',
    'title_asc': 'Title(A-Z)',
    'title_desc': 'Title(Z-A)',
    'classification_type_asc': 'Classification Type(A-Z)',
    'classification_type_desc': 'Classification Type(Z-A)',
    'label_count_asc': 'Label Count | Increasing',
    'label_count_desc': 'Label Count | Decreasing',
    'is_favourite_asc': 'Not Favourite First',
    'is_favourite_desc': 'First Favourite'
  },
  'labels': {
    'default': 'Default',
    'domain_name_asc':'Domain Name(A-Z)',
    'domain_name_desc':'Domain Name(Z-A)',
    'subdomain_name_asc':'Subdomain Name(A-Z)',
    'subdomain_name_desc':'Subdomain Name(Z-A)',
    'is_correct_asc':'Is Correct - False First',
    'is_correct_desc':'Is Correct - True First'
  },
  'criterias': {
    'default': 'Default',
    'uname_asc': 'Name(A-Z)',       
    'uname_desc': 'Name(Z-A)',
    'for_contribution_asc':'For Contribution (-5.0 > 5.0)',
    'for_contribution_desc':'For Contribution (5.0 > -5.0)',
    'correctness_asc':'Correctness (-5.0 > 5.0)',
    'correctness_desc':'Correctness (5.0 > -5.0)',
    'wrongness_asc':'Wrongness (-5.0 > 5.0)',
    'wrongness_desc':'Wrongness (5.0 > -5.0)',
    'count_images_used_asc':'Count of images used-Increasing',
    'count_images_used_desc':'Count of images used-Decreasing'
  }
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
      if detectkey > 0:
        if image_id is None:
          return redirect(url_for(name+"_details_page", key=key))
        return redirect(url_for(name+"_details_page", key=key, image_id=image_id))
    data.init_data()
  
  elif method == 'delete':
    data = all_forms[name](key=key, FK=FK, request = request)
    if request.method == "POST":
      message, key = data.delete()
      if key > 0:
        return redirect(url_for(name+"_index_page"))
  
  elif method == 'details':
    db_ = Database()
    data = db_.select_query_by_id(key, name, name[:-1]+'_id')
  
  elif method == 'index':
    
    sort_by_get = request.args['sort_by'] if 'sort_by' in request.args else 'default'
    search_set = dict()
    for i in request.args:
      if str(i).startswith('search_'):
        search_set[i] = request.args[i]

    db_ = Database()
    if image_id is None:
      data = db_.select_query(name, sort_by=sort_by_get, search=search_set)
    data = db_.select_query(name, data=(image_id, ), sort_by=sort_by_get, search=search_set)
    
    return render_template(name + "/" + method + ".html", 
              data=data, 
              message=message, 
              image_id=image_id, 
              title=str(name).capitalize() + " / " + str(method).capitalize(), 
              sort_by=sort_by[name], 
              selected_sort=sort_by_get,
              search=search_set
    )

  return render_template(name + "/" + method + ".html", data=data, message=message, image_id=image_id, title=str(name).capitalize() + " / " + str(method).capitalize())

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
  user_id = current_user.uid
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
  user_id = current_user.uid
  return form_operation('images', 'add', FK=[('user_id', user_id), ('criteria_id', criteria_id)])

def images_update_page(key):
  return form_operation('images', 'update', key=key)

def images_delete_page(key):
  return form_operation('images', 'delete', key=key)

def images_details_page(key):
  return form_operation('images', 'details', key=key)

def labels_index_page(image_id):
  return form_operation('labels', 'index', FK=[('image_id', image_id)], image_id=image_id)

def labels_add_page(image_id):
  return form_operation('labels', 'add', FK=[('image_id', image_id)], image_id=image_id)

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

def users_delete_page(key):
  return form_operation('users', 'delete', key=key)
  
def users_details_page(key):
  return form_operation('users', 'details', key=key)

def users_change_password_page():
  c_uid = current_user.uid if current_user.is_authenticated else None
  form = ChangePasswordForm(key=c_uid)
  message = ""
  if form.validate_on_submit():
    message, detectkey = form.save()
    flash(message)
    if detectkey > 0:
      return redirect(url_for("logout_page"))
  form.init()
  return render_template('users/change_password.html', data=form, message=message)

def users_update_page(key):
  form = UsersEdit(key=key)
  message = ""
  if form.validate_on_submit():
    message, detectkey = form.save()
    flash(message)
    if detectkey > 0:
      return redirect(url_for("users_index_page"))
  form.init_data()

  return render_template('users/update.html', data=form, message=message)