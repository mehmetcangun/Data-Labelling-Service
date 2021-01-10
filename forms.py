from flask import current_app
import uuid
import os
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, PasswordField, BooleanField, FormField, SubmitField, TextAreaField, RadioField, FileField, FloatField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, NumberRange
from wtforms.fields.html5 import EmailField, URLField, DecimalRangeField, IntegerField
from wtforms_components import IntegerField, ColorField
from flask_login import UserMixin
from werkzeug.utils import secure_filename
from passlib.hash import pbkdf2_sha256 as hasher
from database import Database
from settings import BASE_URL

msgLength   = "The {} has to be between {} and {}"

textFieldStyle = selectFieldStyle= {"class":"focus:bg-indigo-500 focus:text-white px-4 py-1 w-full text-black bg-indigo-50 rounded-lg shadow-lg text-lg"}

colorFieldStyle = {
  "class": "focus:bg-indigo-50 focus:text-black h-20 p-5 m-5 w-full rounded-lg shadow-lg text-lg"
}

radioFieldStyle = {
  "class": "grid grid-flow-col auto-cols-max gap-10 px-4 py-8 my-0 w-full text-indigo-500 bg-indigo-50 rounded-lg shadow-lg text-lg"
}

checkboxFieldStyle = {
  "class": "h-6 w-6 border border-gray-300 rounded-md checked:bg-blue-600 checked:border-transparent focus:outline-none"
}

submitFieldStyle = {"class":"px-6 py-3 font-bold bg-red-500 rounded-md text-white mx-96 hover:bg-red-900"}


class LoginForm(FlaskForm):
  email           = EmailField("E-Mail", validators=[DataRequired(), Length(min=1, max=100, message = msgLength.format("E-Mail", 1, 100))], render_kw=textFieldStyle)
  
  password        = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=50, message = msgLength.format("Password", 8, 50))], render_kw=textFieldStyle)

  submit          = SubmitField(render_kw=submitFieldStyle)

class Users(FlaskForm):
  uname           = StringField("Name", validators=[DataRequired(), Length(min=1, max=30, message = msgLength.format("Name", 1, 30))], render_kw=textFieldStyle)
  
  surname         = StringField("Surname", validators=[DataRequired(), Length(min=1, max=30, message = msgLength.format("Surname", 1, 30))], render_kw=textFieldStyle)

  email           = EmailField("E-Mail", validators=[DataRequired(), Length(min=1, max=100, message = msgLength.format("E-Mail", 1, 100))], render_kw=textFieldStyle)
  
  password        = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=50, message = msgLength.format("Password", 8, 50)), EqualTo('password_repeat', message='Password must match.')], render_kw=textFieldStyle)
  
  password_repeat = PasswordField("Password Repeat", render_kw=textFieldStyle)
  
  security_answer = StringField("What's your favorite object or person?", validators=[DataRequired(),  Length(min=1, max=30, message = msgLength.format("What's your favorite object or person?", 1, 30))], render_kw=textFieldStyle)

class UsersEdit(FlaskForm):
  key=None
  def __init__(self, *args, **kwargs):
    super(UsersEdit, self).__init__(*args, **kwargs)
    self.key     = kwargs['key']
  
  uname           = StringField("Name", validators=[DataRequired(), Length(min=1, max=30, message = msgLength.format("Name", 1, 30))], render_kw=textFieldStyle)
  
  surname         = StringField("Surname", validators=[DataRequired(), Length(min=1, max=30, message = msgLength.format("Surname", 1, 30))], render_kw=textFieldStyle)

  email           = EmailField("E-Mail", validators=[DataRequired(), Length(min=1, max=100, message = msgLength.format("E-Mail", 1, 100))], render_kw=textFieldStyle)
  
  security_answer = StringField("What's your favorite object or person?", validators=[DataRequired(),  Length(min=1, max=30, message = msgLength.format("What's your favorite object or person?", 1, 30))], render_kw=textFieldStyle)

  submit = SubmitField(render_kw=submitFieldStyle)

  def init_data(self):
    if self.key is not None:
      db_ = Database()
      db_data = db_.select_query_by_id(self.key, 'users', 'user_id')
      self.uname.data             = db_data['uname']
      self.surname.data           = db_data['surname']
      self.email.data             = db_data['email']
      self.security_answer.data   = db_data['security_answer']

  def save(self):
    cp = self.data
    cp.pop('csrf_token', None)
    cp.pop('submit', None)
    
    data = {
      'primary_key': 'user_id',
      'table_name': 'users',
      'data': cp,
      'where': {
        'user_id': self.key
      }
    }
    db_ = Database()
    return db_.update(data)

class UsersForm(FlaskForm):
  key = FK = request = None
  def __init__(self, *args, **kwargs):
    super(UsersForm, self).__init__(*args, **kwargs)
    self.key     = kwargs['key']
    self.FK      = kwargs['FK']
    self.request = kwargs['request']
  
  form = FormField(Users)
  submit = SubmitField(render_kw=submitFieldStyle)

  def save(self):
    cp = self.form.data
    cp.pop('csrf_token', None)
    cp.pop('password_repeat', None)
    
    if self.key is None:
      cp['password'] = hasher.hash(cp['password'])
    else:
      cp.pop('password', None)

    if self.FK is not None:
      for i in self.FK:
        cp[i[0]] = i[1]
    
    data = {
      'primary_key': 'user_id',
      'table_name': 'users',
      'data': cp,
      'where': {
        'user_id': self.key
      }
    }
    db_ = Database()
    if self.key is None:
      return db_.add(data)
    return db_.update(data)
  
  def delete(self):
    data = {
      'primary_key': 'user_id',
      'table_name': 'users',
      'data': [],
      'where': {
        'user_id': self.key
      }
    }
    if self.key is not None:
      db_ = Database()
      return db_.delete(data)

class ChangePasswordForm(FlaskForm):
  key = None
  def __init__(self, *args, **kwargs):
    super(ChangePasswordForm, self).__init__(*args, **kwargs)
    self.key = kwargs['key']

  email           = EmailField("E-Mail", validators=[DataRequired(), Length(min=1, max=100, message = msgLength.format("E-Mail", 1, 100))], render_kw=textFieldStyle)

  security_answer = StringField("What's your favorite object or person?", validators=[DataRequired(),  Length(min=1, max=30, message = msgLength.format("What's your favorite object or person?", 1, 30))], render_kw=textFieldStyle)
  
  password        = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=50, message = msgLength.format("Password", 8, 50)), EqualTo('password_repeat', message='Password must match.')], render_kw=textFieldStyle)
  
  password_repeat = PasswordField("Password Repeat", render_kw=textFieldStyle)
  
  submit          = SubmitField(render_kw=submitFieldStyle)
  
  def init(self):
    if self.key is not None:
      db_ = Database()
      users = db_.select_query_by_id(self.key, 'users', 'user_id')
      for i in users:
        print("OBAAA: ", i)
      self.email.data = users['email']
      self.security_answer.data = users['security_answer']
    else:
      print("kel")
      
  def save(self):
    cp = self.data
    cp.pop('submit', None)
    cp.pop('csrf_token', None)
    cp.pop('password_repeat', None)
    
    cp['password'] = hasher.hash(cp['password'])
    d_email = cp['email']
    cp.pop('email', None)
    d_security_answer = cp['security_answer']
    cp.pop('security_answer', None)

    data = {
      'primary_key': 'user_id',
      'table_name': 'users',
      'data': cp,
      'where': {
        'email': d_email,
        'security_answer': d_security_answer 
      }
    }
    db_ = Database()
    return db_.update(data)

class Domains(FlaskForm):
  domain_id = None
  
  domain_name = StringField("Domain Name", validators=[DataRequired(), Length(min=1, max=50, message = msgLength.format("Domain Name", 1, 50))], render_kw=textFieldStyle)
  
  description = TextAreaField("Description", validators = [DataRequired(), Length(min=1, max=1000, message= msgLength.format("Description", 1, 1000))], render_kw=textFieldStyle)
  
  domain_priority_rate = RadioField("Priority Rate(10 higher rate than 1)", default=1, coerce=int, choices=[x for x in range(1, 11)], render_kw=radioFieldStyle)
  
  color = ColorField("Color", validators = [DataRequired()], render_kw=colorFieldStyle)

class DomainsForm(FlaskForm):
  key = FK = request = None
  def __init__(self, *args, **kwargs):
    super(DomainsForm, self).__init__(*args, **kwargs)
    self.key     = kwargs['key']
    self.FK      = kwargs['FK']
    self.request = kwargs['request']
  
  form = FormField(Domains)
  submit = SubmitField(render_kw=submitFieldStyle)
  
  def init_data(self):
    if self.key is not None:
      domain = Database()
      domains = domain.select_query_by_id(self.key, 'domains', 'domain_id')
      self.form['domain_name'].data          = domains['domain_name']
      self.form['description'].data   = domains['description']
      self.form['domain_priority_rate'].data = domains['domain_priority_rate']
      self.form['color'].data         = domains['color']
  
  
  def save(self):
    cp = self.form.data
    cp.pop('csrf_token', None)
    
    cp['color'] = self.request.form['form-color']

    data = {
      'primary_key': 'domain_id',
      'table_name': 'domains',
      'data': cp,
      'where': {
        'domain_id': self.key
      }
    }
    db_ = Database()
    if self.key is None:
      return db_.add(data)
    return db_.update(data)
  
  def delete(self):
    data = {
      'primary_key': 'domain_id',
      'table_name': 'domains',
      'data': [],
      'where': {
        'domain_id': self.key
      }
    }
    if self.key is not None:
      db_ = Database()
      return db_.delete(data)

class Subdomains(FlaskForm):
  subdomain_name = StringField("Subdomain Name", validators=[DataRequired(), Length(min=1, max=50, message = msgLength.format("Subdomain Name", 1, 50))], render_kw=textFieldStyle)

  subdomain_priority_rate = RadioField("Priority Rate(10 higher rate than 1)", default=1, coerce=int, choices=[x for x in range(1, 11)], render_kw=radioFieldStyle)

  icon = StringField("icon", validators=[Optional()], render_kw=textFieldStyle)

  frontcolor = ColorField("Front Color of Icon", default="#000000", validators = [], render_kw=colorFieldStyle)
  
  backgroundcolor = ColorField("Background Color of Icon", default="#FFFFFF", validators = [], render_kw=colorFieldStyle)

class SubdomainsForm(FlaskForm):
  key = FK = request = None
  def __init__(self, *args, **kwargs):
    super(SubdomainsForm, self).__init__(*args, **kwargs)
    self.key     = kwargs['key']
    self.FK      = kwargs['FK']
    self.request = kwargs['request']
  
  form = FormField(Subdomains)
  submit = SubmitField(render_kw=submitFieldStyle)
  domains = None
  domain_id = None
  def init_data(self):
    if self.key is not None:
      db_ = Database()
      subdomains = db_.select_query_by_id(self.key, 'subdomains', 'subdomain_id')
      self.form['subdomain_name'].data           = subdomains['subdomain_name']
      self.form['subdomain_priority_rate'].data  = subdomains['subdomain_priority_rate']
      self.form['icon'].data                     = subdomains['icon']
      self.form['frontcolor'].data               = subdomains['frontcolor']
      self.form['backgroundcolor'].data          = subdomains['backgroundcolor']
      
      self.domains = db_.select_query('domains')
      self.domain_id = subdomains['domain_id']
  
  def save(self):
    cp = self.form.data
    cp.pop('csrf_token', None)
    
    cp['frontcolor'] = self.request.form['form-frontcolor']
    cp['backgroundcolor'] = self.request.form['form-backgroundcolor']

    if self.FK is not None:
      for i in self.FK:
        cp[i[0]] = i[1]
    
    if 'domain_select' in self.request.form:
      cp['domain_id'] = self.request.form['domain_select']

    data = {
      'primary_key': 'subdomain_id',
      'table_name': 'subdomains',
      'data': cp,
      'where': {
        'subdomain_id': self.key
      }
    }
    print(data)
    db_ = Database()
    if self.key is None:
      return db_.add(data)
    return db_.update(data)
  
  def delete(self):
    data = {
      'primary_key': 'subdomain_id',
      'table_name': 'subdomains',
      'data': [],
      'where': {
        'subdomain_id': self.key
      }
    }
    if self.key is not None:
      db_ = Database()
      return db_.delete(data)

class Criterias(FlaskForm):
  for_contribution  = FloatField("For Contribution", default=1.0, validators=[DataRequired(), NumberRange(min=-5.0, max=5.0, message = msgLength.format("For Contribution", -5.0, 5.0))], render_kw=textFieldStyle)
  correctness       = FloatField("Correctness", default=0.0, validators=[DataRequired(), NumberRange(min=-5, max=5, message = msgLength.format("Correctness", -5.0, 5.0))], render_kw=textFieldStyle)
  wrongness         = FloatField("Wrongness", default=0.0, validators=[DataRequired(), NumberRange(min=-5, max=5, message = msgLength.format("Wrongness", -5.0, 5.0))], render_kw=textFieldStyle)

class CriteriasForm(FlaskForm):
  key = FK = request = None
  def __init__(self, *args, **kwargs):
    super(CriteriasForm, self).__init__(*args, **kwargs)
    self.key     = kwargs['key']
    self.FK      = kwargs['FK']
    self.request = kwargs['request']
  
  form = FormField(Criterias)
  submit = SubmitField(render_kw=submitFieldStyle)

  def init_data(self):
    if self.key is not None:
      db_ = Database()
      db_data = db_.select_query_by_id(self.key, 'criterias', 'criteria_id')
      self.form['for_contribution'].data   = db_data['for_contribution']
      self.form['correctness'].data        = db_data['correctness']
      self.form['wrongness'].data          = db_data['wrongness']
  
  def save(self):
    cp = self.form.data
    cp.pop('csrf_token', None)

    if self.FK is not None:
      for i in self.FK:
        cp[i[0]] = i[1]
    
    data = {
      'primary_key': 'criteria_id',
      'table_name': 'criterias',
      'data': cp,
      'where': {
        'criteria_id': self.key
      }
    }
    db_ = Database()
    if self.key is None:
      return db_.add(data)
    return db_.update(data)
  
  def delete(self):
    data = {
      'primary_key': 'criteria_id',
      'table_name': 'criterias',
      'data': [],
      'where': {
        'criteria_id': self.key
      }
    }
    if self.key is not None:
      db_ = Database()
      return db_.delete(data)

class Images(FlaskForm):
  title                 = StringField("Title", validators=[DataRequired(), Length(min=1, max=50, message = msgLength.format("Title", 1, 250))], render_kw=textFieldStyle)

  upload_image          = FileField("Image File", render_kw={'accept': '.jpg, .jpeg, .png'})
  
  url_path              = URLField("Image Url(if file not found)", validators=[Length(min=0, max=1000, message = msgLength.format("Image Url", 0, 1000))], render_kw=textFieldStyle)
  
  most_contribution     = IntegerField("Most Contribution(by labeller)", default=1, validators=[DataRequired(), NumberRange(min=1, message="The contibution size must be greater than 1")], render_kw=textFieldStyle)
  
  classification_type   = SelectField("Classification Type", choices = [("Binary Classification", "Binary Classification"), ("Multi-Class", "Multi-Class"), ("Multi-Label","Multi-Label")], render_kw=selectFieldStyle)
  
  is_favourite          = BooleanField("Is your favourite image?", default=False, validators=[], render_kw=checkboxFieldStyle)

class ImagesForm(FlaskForm):
  key = FK = request = None
  def __init__(self, *args, **kwargs):
    super(ImagesForm, self).__init__(*args, **kwargs)
    self.key     = kwargs['key']
    self.FK      = kwargs['FK']
    self.request = kwargs['request']
  
  form = FormField(Images)
  submit = SubmitField(render_kw=submitFieldStyle)

  criterias = None
  criteria_id = None

  def init_data(self):
    if self.key is not None:
      db_ = Database()
      db_data = db_.select_query_by_id(self.key, 'images', 'image_id')
      self.form['title'].data                  = db_data['title']
      self.form['url_path'].data               = db_data['url_path']
      self.form['most_contribution'].data      = db_data['most_contribution']
      self.form['classification_type'].data    = db_data['classification_type']
      self.form['is_favourite'].data           = db_data['is_favourite']
      
      self.criterias = db_.select_query('criterias')
      self.criteria_id = db_data['criteria_id']

  def save(self):
    cp = self.form.data
    file = self.form['upload_image'].data.filename
    url = self.form['url_path'].data

    if not file and not url:
      return "Image is not uploaded or Image url is not given.", -1

    if file:
      filename = './static/uploads/' + secure_filename(str(uuid.uuid1())+'.jpg')
      image_data = self.request.files['form-upload_image'].read()
      open(filename, 'wb').write(image_data)
      cp['url_path'] = BASE_URL+filename[1:]

    cp.pop('csrf_token', None)
    cp.pop('upload_image', None)

    if self.FK is not None:
      for i in self.FK:
        cp[i[0]] = i[1]
    
    if 'selected_criteria' in self.request.form:
      cp['criteria_id'] = self.request.form['selected_criteria']

    data = {
      'primary_key': 'image_id',
      'table_name': 'images',
      'data': cp,
      'where': {
        'image_id': self.key
      }
    }
    db_ = Database()
    if self.key is None:
      return db_.add(data)
    return db_.update(data)
  
  def delete(self):
    data = {
      'primary_key': 'image_id',
      'table_name': 'images',
      'data': [],
      'where': {
        'image_id': self.key
      }
    }
    if self.key is not None:
      db_ = Database()
      
      img_url = str(db_.select_query_by_id(self.key, 'images', 'image_id')['url_path'])
      msg, key = db_.delete(data)
      if key > 0:
        if img_url.startswith('/static/uploads/'):
          os.remove('.'+img_url)
      return msg, key

class Labels(FlaskForm):
  is_correct = BooleanField('Is it correct?', default=False, validators=[],render_kw=checkboxFieldStyle)

class LabelsForm(FlaskForm):
  key = FK = request = None
  subdomains = None
  def __init__(self, *args, **kwargs):
    super(LabelsForm, self).__init__(*args, **kwargs)
    self.key     = kwargs['key']
    self.FK      = kwargs['FK']
    self.request = kwargs['request']
    
    subdomains = Database()
    self.subdomains = subdomains.select_query(name="subdomains_for_label", data=[(self.FK[0][1],)])
  
  form = FormField(Labels)
  submit = SubmitField(render_kw=submitFieldStyle)

  def init_data(self):
    if self.key is not None:
      db_ = Database()
      db_data = db_.select_query_by_id(self.key, 'labels', 'label_id')
      self.form['is_correct'].data             = db_data['is_correct']
  
  def save(self):
    cp = self.form.data
    cp.pop('csrf_token', None)

    if self.FK is not None:
      for i in self.FK:
        cp[i[0]] = i[1]
    
    if 'subdomain_id' in self.request.form:
      cp['subdomain_id'] = self.request.form['subdomain_id']
    
    data = {
      'primary_key': 'label_id',
      'table_name': 'labels',
      'data': cp,
      'where': {
        'label_id': self.key
      }
    }
    db_ = Database()
    if self.key is None:
      return db_.add(data)
    return db_.update(data)
  
  def delete(self):
    data = {
      'primary_key': 'label_id',
      'table_name': 'labels',
      'data': [],
      'where': {
        'label_id': self.key
      }
    }
    if self.key is not None:
      db_ = Database()
      return db_.delete(data)

'''
class Contributions(FlaskForm):
  reported = SelectField(
    "Reported",
    choices = [("blur image", "blur image"), ("no image", "no image"), ("no correct answer", "no correct answer")],
    render_kw = { "class" : "form-control"}
  )
  extra_info = TextAreaField(
    "Extra Information", 
    validators = [ 
      DataRequired(message = msgRequired.format("Extra Information")),
      Length(min=1, max=1500, message = msgLength.format("Extra Information", 1, 1500))
    ],
    render_kw = { "class" : "form-control" }
  )
'''