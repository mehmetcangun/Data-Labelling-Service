from flask import current_app, redirect, url_for, render_template, request, abort
from forms import LoginForm, UsersEdit, ChangePasswordForm, DomainsForm, SubdomainsForm, CriteriasForm, ImagesForm, LabelsForm, UsersForm

from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from passlib.hash import pbkdf2_sha256 as hasher

from functools import wraps
from database import Database


class User(UserMixin):
  def __init__(self, email, password):
    self.email = email
    self.password = password
    self.is_admin = False
    self.uid = None
    self.name = None
    self.points = 0
  
  def get_id(self):
    return self.email
  
  def get_uid(self):
    return self.uid

def login_page():
  message = None
  form = LoginForm()
  if form.validate_on_submit():
    email = form['email'].data
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
    message = "Invalid credentials."
  return render_template("login.html", data=form, message=message)

def get_user(user_email):
  db = Database()
  user_ = db.select_query_by_id(user_email, "users", where="email")
  if user_ is not None:
    user = User(user_email, user_['password'])
    user.is_admin = True if user_['usertype'] == 0 else False
    user.uid = user_['user_id']
    user.name = user_['uname']
    user.points = user_['points']
    return user
  return None

@login_required
def logout_page():
  logout_user()
  return redirect(url_for("home_page"))


def admin_required(f):
  
  @login_required
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

import psycopg2 as dbapi2
import os
DB_URL = os.getenv("DATABASE_URL")

def update_whole_points(user_id):
  query = """
    update users set points =
    CASE WHEN ((select count(*) from contributions where contributions.user_id = %s) = 0) THEN 0
    ELSE (select SUM(points) from (select for_contribution + correctness * COALESCE((
           select count((domain_id, image_id))
           FROM (select l.label_id, l.image_id, d.domain_id, is_correct
                    from labels as l
                             inner join subdomains as s on s.subdomain_id = l.subdomain_id
                             inner join domains as d on d.domain_id = s.domain_id
                    group by l.image_id, d.domain_id, l.label_id
                    INTERSECT
                    select l.label_id, l.image_id, d.domain_id, true as is_correct
                    from labels as l
                             inner join subdomains as s on s.subdomain_id = l.subdomain_id
                             inner join domains as d on d.domain_id = s.domain_id
                             inner join contributions as c on c.label_id = l.label_id
                    where c.user_id = %s
                    group by l.image_id, d.domain_id, l.label_id
                ) as calc
           where domain_id = d.domain_id
             and image_id = l.image_id
             and is_correct = true
           group by domain_id, image_id
       ), 0) - wrongness * (count((d.domain_id, l.image_id)) - COALESCE((
       select count((domain_id, image_id))
       FROM (select l.label_id, l.image_id, d.domain_id, is_correct
                from labels as l
                         inner join subdomains as s on s.subdomain_id = l.subdomain_id
                         inner join domains as d on d.domain_id = s.domain_id
                group by l.image_id, d.domain_id, l.label_id
                INTERSECT
                select l.label_id, l.image_id, d.domain_id, true as is_correct
                from labels as l
                         inner join subdomains as s on s.subdomain_id = l.subdomain_id
                         inner join domains as d on d.domain_id = s.domain_id
                         inner join contributions as c on c.label_id = l.label_id
                where c.user_id = %s
                group by l.image_id, d.domain_id, l.label_id
            ) as calc2
       where domain_id = d.domain_id
         and image_id = l.image_id
         and is_correct = true
       group by domain_id, image_id
   ), 0)) as points
      from labels as l
               inner join subdomains as s on s.subdomain_id = l.subdomain_id
               inner join domains as d on d.domain_id = s.domain_id
               inner join images as i on i.image_id = l.image_id
               inner join criterias as c on c.criteria_id = i.criteria_id
      group by l.image_id, d.domain_id, c.criteria_id
) as result)
END

where user_id = %s

  """
  with dbapi2.connect(DB_URL) as connection:
    with connection.cursor() as cursor:
      cursor.execute(query, (user_id, user_id, user_id, user_id, ))
      connection.commit()

def home_page():
  data = None
  user_id = current_user.uid if current_user.is_authenticated else -1
  
  parameters = [user_id]
  query = """
    select i.image_id, url_path, for_contribution,correctness, wrongness, count(l.label_id) as label_size,
        most_contribution - (select count(*) from contributions as c inner join labels as l on c.label_id = l.label_id
        inner join users as u on u.user_id = c.user_id inner join images as m_i on m_i.image_id = l.image_id
        where i.image_id = m_i.image_id) as remaining_size
    from images as i inner join criterias as c on i.criteria_id = c.criteria_id
        left join labels as l on l.image_id = i.image_id
        left join subdomains as s on s.subdomain_id = l.subdomain_id
    where most_contribution > (select count(*) from contributions as c
        inner join labels as l on c.label_id = l.label_id inner join users as u on u.user_id = c.user_id
        inner join images as m_i on m_i.image_id = l.image_id 
        where i.image_id = m_i.image_id
    )
    group by i.image_id, c.criteria_id
    order by RANDOM()
    LIMIT 50
    """

  with dbapi2.connect(DB_URL) as connection:
    with connection.cursor() as cursor:
      cursor.execute(query, tuple(parameters))
      result = cursor.fetchall()
      header = list( cursor.description[i][0] for i in range(0, len(cursor.description)) )
      result_with_header = list()
      for i in result:
        result_with_header.append(dict(zip(header, i)))
      data  = result_with_header
  
  return render_template('home.html', data=data)

@login_required
def contribute_add_page(image_id, domain_id=None):
  
  if request.method == 'POST':
    selected_labels = request.form.getlist('label_id')
    db_ = Database()
    for i in selected_labels:
      data = {
        'primary_key': 'contribution_id',
        'table_name': 'contributions',
        'data': {
          'user_id': current_user.uid,
          'label_id': int(i)
        },
        'where': {}
      }
      db_.add(data)
    return redirect(url_for("profile_page"))
  
  message = None
  parameters = [image_id]
  states = [
    "Select the domain for contribution",
    "Select the most appropriate labels for an image"
  ]
  if domain_id is not None:
    count = 0
    query = """select count(distinct d.domain_id) from contributions as c
        inner join labels as l on l.label_id = c.label_id
        inner join subdomains as s on l.subdomain_id = s.subdomain_id
        inner join domains as d on d.domain_id = s.domain_id
      where user_id = %s and d.domain_id = %s and l.image_id = %s """
    
    with dbapi2.connect(DB_URL) as connection:
      with connection.cursor() as cursor:
        cursor.execute(query, (current_user.uid, domain_id, image_id, ))
        count = cursor.fetchone()[0]
        print(current_user.uid, " ", count)

    if count == 0:
      query = """select l.label_id as label_id, l.image_id as image_id, icon, url_path, d.domain_id as domain_id, domain_name, color, subdomain_name, s.subdomain_id as subdomain_id, frontcolor, backgroundcolor
          from labels as l inner join subdomains as s on l.subdomain_id = s.subdomain_id
          inner join domains as d on d.domain_id = s.domain_id
          inner join images as i on i.image_id = l.image_id
      where l.image_id = %s and d.domain_id = %s"""
      parameters.append(domain_id)
    else:
      domain_id = None
      message = "The contribution is done before, please select another domain."

  
  state_key = 0
  state = states[0]
  if domain_id is not None:
    state = states[1]
    state_key = 1
  else:
    query = """
      select distinct d.domain_id as domain_id, l.image_id as image_id, url_path, domain_name, color
        from labels as l inner join subdomains as s on l.subdomain_id = s.subdomain_id
        inner join domains as d on d.domain_id = s.domain_id
        inner join images as i on i.image_id = l.image_id
      where l.image_id = %s
    """

  data = None
  with dbapi2.connect(DB_URL) as connection:
    with connection.cursor() as cursor:
      cursor.execute(query, tuple(parameters))
      result = cursor.fetchall()
      header = list( cursor.description[i][0] for i in range(0, len(cursor.description)) )
      result_with_header = list()
      for i in result:
        result_with_header.append(dict(zip(header, i)))
      data  = result_with_header
  
  return render_template('contributions/make_contribution.html', data=data, state=state, state_key=state_key, message=message)

def profile_page(user_id=None):
  profile_id = current_user.uid if user_id is None and current_user.is_authenticated else user_id
  update_whole_points(profile_id)

  db_ = Database()
  profile_info = db_.select_query_by_id(profile_id, "users", "user_id")
  parameters = [profile_id]
  query = """
    select i.image_id, i.url_path, count(distinct d.domain_id) as cont_size
      from contributions as c
          inner join labels as l on c.label_id = l.label_id
          inner join images as i on l.image_id = i.image_id
          inner join subdomains as s on s.subdomain_id = l.subdomain_id
          inner join domains as d on d.domain_id = s.domain_id
      where c.user_id = %s
      group by i.image_id
    """
  with dbapi2.connect(DB_URL) as connection:
    with connection.cursor() as cursor:
      cursor.execute(query, tuple(parameters))
      result = cursor.fetchall()
      header = list( cursor.description[i][0] for i in range(0, len(cursor.description)) )
      result_with_header = list()
      for i in result:
        result_with_header.append(dict(zip(header, i)))
      data  = result_with_header 
  return render_template('users/profile.html', data=data, profile_info=profile_info)


def form_operation(name, method, key=None, only_admin=True, FK=None, image_id=None):
  data = None
  message = ""
  if method == 'add':
    data = all_forms[name](key=key, FK=FK, request = request)
    if data.validate_on_submit():
      message, key = data.save()
      if key != -1:
        if image_id is None:
          return redirect(url_for(name+"_index_page"))
        return redirect(url_for(name+"_index_page", image_id=image_id))
  
  elif method == 'update':
    data = all_forms[name](key=key, FK=FK, request = request)
    if data.validate_on_submit():
      message, detectkey = data.save()
      if detectkey > 0:
        if image_id is None:
          return redirect(url_for(name+"_index_page"))
        return redirect(url_for(name+"_index_page", image_id=image_id))
    data.init_data()
  
  elif method == 'delete':
    data = all_forms[name](key=key, FK=FK, request = request)
    if request.method == "POST":
      message, key = data.delete()
      if key > 0:
        if image_id is None:
          return redirect(url_for(name+"_index_page"))
        return redirect(url_for(name+"_index_page", image_id=image_id))
  
  elif method == 'details':
    db_ = Database()
    data = db_.select_query_by_id(key, name, name[:-1]+'_id')
    print(data, " ", key)

  elif method == 'index':
    
    sort_by_get = request.args['sort_by'] if 'sort_by' in request.args else 'default'
    search_set = dict()
    for i in request.args:
      if str(i).startswith('search_'):
        search_set[i] = request.args[i]

    db_ = Database()
    if image_id is None:
      data = db_.select_query(name, sort_by=sort_by_get, search=search_set, data=[])
    else:
      data = db_.select_query(name, data=[image_id, ], sort_by=sort_by_get, search=search_set)
    
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

@admin_required
def domains_index_page():
  return form_operation('domains', 'index')

@admin_required
def domains_add_page():
  return form_operation('domains', 'add')

@admin_required
def domains_update_page(key):
  return form_operation('domains', 'update', key=key)

@admin_required
def domains_delete_page(key):
  return form_operation('domains', 'delete', key=key)

@admin_required
def domains_details_page(key):
  return form_operation('domains', 'details', key=key)

@admin_required
def subdomains_index_page():
  return form_operation('subdomains', 'index')

@admin_required
def subdomains_add_page(domain_id):
  return form_operation('subdomains', 'add', FK=[('domain_id', domain_id)])

@admin_required
def subdomains_update_page(key):
  return form_operation('subdomains', 'update', key=key)

@admin_required
def subdomains_delete_page(key):
  return form_operation('subdomains', 'delete', key=key)

@admin_required
def subdomains_details_page(key):
  return form_operation('subdomains', 'details', key=key)

@admin_required
def criterias_index_page():
  return form_operation('criterias', 'index')

@admin_required
def criterias_add_page():
  user_id = current_user.uid
  return form_operation('criterias', 'add', FK=[('user_id', user_id)])

@admin_required
def criterias_update_page(key):
  return form_operation('criterias', 'update', key=key)

@admin_required
def criterias_delete_page(key):
  return form_operation('criterias', 'delete', key=key)

@admin_required
def criterias_details_page(key):
  return form_operation('criterias', 'details', key=key)

@admin_required
def images_index_page():
  return form_operation('images', 'index')

@admin_required
def images_add_page(criteria_id):
  user_id = current_user.uid
  return form_operation('images', 'add', FK=[('user_id', user_id), ('criteria_id', criteria_id)])

@admin_required
def images_update_page(key):
  return form_operation('images', 'update', key=key)

@admin_required
def images_delete_page(key):
  return form_operation('images', 'delete', key=key)

@admin_required
def images_details_page(key):
  return form_operation('images', 'details', key=key)

@admin_required
def labels_index_page(image_id):
  return form_operation('labels', 'index', FK=[('image_id', image_id)], image_id=image_id)

@admin_required
def labels_add_page(image_id):
  return form_operation('labels', 'add', FK=[('image_id', image_id)], image_id=image_id)

@admin_required
def labels_update_page(image_id, key):
  return form_operation('labels', 'update', key=key, FK=[('image_id', image_id)], image_id=image_id)

@admin_required
def labels_delete_page(image_id, key):
  return form_operation('labels', 'delete', key=key, FK=[('image_id', image_id)], image_id=image_id)

@admin_required
def labels_details_page(image_id, key):
  return form_operation('labels', 'details', key=key, FK=[('image_id', image_id)], image_id=image_id)

@admin_required
def users_index_page():
  return form_operation('users', 'index')

def users_add_page(usertype):
  return form_operation('users', 'add', FK=[('usertype', usertype-8)])

@admin_required
def users_delete_page(key):
  return form_operation('users', 'delete', key=key)

@admin_required
def users_details_page(key):
  return redirect(url_for("profile_page", user_id=key))

def users_change_password_page():
  c_uid = current_user.uid if current_user.is_authenticated else None
  form = ChangePasswordForm(key=c_uid)
  message = ""
  if form.validate_on_submit():
    message, detectkey = form.save()
    if detectkey > 0:
      return redirect(url_for("logout_page"))
  form.init()
  return render_template('users/change_password.html', data=form, message=message)

@login_required
def users_update_page(key):
  if not current_user.is_admin and key != current_user.uid:
    return redirect(url_for("home_page"))
  
  form = UsersEdit(key=key)
  message = ""
  if form.validate_on_submit():
    message, detectkey = form.save()
    if detectkey > 0:
      if form['email'].data != current_user.email:
        return redirect(url_for("login_page"))
      else:
        return redirect(url_for("profile_page"))
  form.init_data()
  return render_template('users/update.html', data=form, message=message)