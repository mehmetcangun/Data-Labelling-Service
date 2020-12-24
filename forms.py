from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, PasswordField, BooleanField, FormField, SubmitField, TextAreaField, RadioField, FileField, FloatField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, NumberRange
from wtforms.fields.html5 import EmailField, URLField, DecimalRangeField, IntegerField
from wtforms_components import IntegerField, ColorField
from werkzeug.utils import secure_filename
import uuid
import os

msgRequired = "The {} must be filled."
msgLength   = "The {} has to be between {} and {}"

class LoginForm(FlaskForm):
  #email = EmailField("E-Mail", validators=[DataRequired()])
  username = StringField("Username", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])

class Register(FlaskForm):
  name = StringField("Name", validators=[DataRequired()])
  surname = StringField("Surname", validators=[DataRequired()])
  email = EmailField("E-Mail", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired(), EqualTo('password_repeat', message='Password must match.')])
  password_repeat = PasswordField("Password Repeat", validators=[DataRequired()])

class RegisterForm(FlaskForm):
  register = FormField(Register)
  submit  = SubmitField( render_kw = { "class" : "btn-primary"})


class Domains(FlaskForm):
  domain_id = None
  name = StringField("Name", validators=[DataRequired()])
  description = TextAreaField(
    "Description", 
    validators = [ 
      DataRequired(message = msgRequired.format("Description")),
      Length(min=1, max=1000, message = msgLength.format("Description", 1, 1000))
    ],
    render_kw = { "class" : "form-control" }
  )
  priority_rate = RadioField(
    "Priority Rate(10 higher rate than 1)",
    default = 1,
    coerce=int,
    choices = [ x for x in range(1, 11) ],
    render_kw = { "class" : "list-group list-group-horizontal" }
  )
  color = ColorField(
    "Color", 
    validators = [],
    render_kw = { "class" : "form-control"}
  )

from database import Database
class DomainsForm(FlaskForm):
  
  form = FormField(Domains)
  submit  = SubmitField( render_kw = { "class" : "btn-primary"})
  
  key = None
  def init_key(self, **keys):
    self.key = keys['key']

  def init_data(self):
    if self.key is not None:
      domain = Database()
      domains = domain.select_query_by_id(self.key, 'domains', 'domain_id')
      self.form['name'].data          = domains['name']
      self.form['description'].data   = domains['description']
      self.form['priority_rate'].data = domains['priority_rate']
      self.form['color'].data         = domains['color']
  
  
  def save(self):
    cp = self.form.data
    cp.pop('csrf_token', None)
    cp['color'] = str(cp['color'])
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
  name = StringField("name", validators=[DataRequired()])
  priority_rate = RadioField(
    "Priority Rate(10 higher rate than 1)",
    default = 1,
    coerce=int,
    choices = [ x for x in range(1, 11) ],
    render_kw = { "class" : "list-group list-group-horizontal" }
  )
  icon = StringField("icon", validators=[Optional()])

class SubdomainsForm(FlaskForm):
  form = FormField(Subdomains)
  submit  = SubmitField( render_kw = { "class" : "btn-primary"})

  key = None
  FKDomainId = None
  
  def init_key(self, **keys):
    self.key = keys['key']
    self.FKDomainId = keys['FK']

  def init_data(self):
    if self.key is not None:
      subdomain = Database()
      subdomains = subdomain.select_query_by_id(self.key, 'subdomains', 'subdomain_id')
      self.form['name'].data           = subdomains['name']
      self.form['priority_rate'].data  = subdomains['priority_rate']
      self.form['icon'].data           = subdomains['icon']
  
  def save(self):
    cp = self.form.data
    cp.pop('csrf_token', None)
    if self.FKDomainId is not None:
      for i in self.FKDomainId:
        cp[i[0]] = i[1]
    
    data = {
      'primary_key': 'subdomain_id',
      'table_name': 'subdomains',
      'data': cp,
      'where': {
        'subdomain_id': self.key
      }
    }
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
  for_contribution  = FloatField("For Contribution", validators=[ NumberRange(min=-5.0, max=5.0)])
  correctness       = FloatField("Correctness", validators=[ NumberRange(min=-5, max=5)])
  wrongness         = FloatField("Wrongness", validators=[ NumberRange(min=-5, max=5)])
  reported          = FloatField("Reported", validators=[ NumberRange(min=-5, max=5)])
  extra_info        = FloatField("Extra Information", validators=[ NumberRange(min=-5, max=5)])

class CriteriasForm(FlaskForm):
  form = FormField(Criterias)
  submit  = SubmitField( render_kw = { "class" : "btn-primary"})

  key = None
  FK = None
  
  def init_key(self, **keys):
    self.key = keys['key']
    self.FK = keys['FK']

  def init_data(self):
    if self.key is not None:
      db_ = Database()
      db_data = db_.select_query_by_id(self.key, 'criterias', 'criteria_id')
      self.form['for_contribution'].data   = db_data['for_contribution']
      self.form['correctness'].data        = db_data['correctness']
      self.form['wrongness'].data          = db_data['wrongness']
      self.form['reported'].data           = db_data['reported']
      self.form['extra_info'].data         = db_data['extra_info']

      # self.form[''].data           = db_data['']
  
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


class Labels(FlaskForm):
  is_correct = BooleanField("Correct")

class Images(FlaskForm):
  title                 = StringField("Title", validators=[DataRequired()])
  upload_image          = FileField("Image File", validators=[], render_kw={'accept': '.jpg'})
  url_path              = URLField("Image Url(if file not found)")
  most_contribution     = IntegerField("Most Contribution(by labeller)", validators=[NumberRange(min=1, message="The contibution size must be greater than 1")])
  classification_type   = SelectField(
    "Classification Type",
    choices = [("Binary Classification", "Binary Classification"), ("Multi-Class", "Multi-Class"), ("Multi-Label","Multi-Label")],
    render_kw = { "class" : "form-control"}
  )

class ImagesForm(FlaskForm):
  form = FormField(Images)
  submit  = SubmitField( render_kw = { "class" : "btn-primary"})

  criterias = None
  criteria_id = None

  key = None
  FK = None
  request = None

  def init_key(self, **keys):
    self.key = keys['key']
    self.FK = keys['FK']
    self.request = keys['request']

  def init_data(self):
    if self.key is not None:
      db_ = Database()
      db_data = db_.select_query_by_id(self.key, 'images', 'image_id')
      self.form['title'].data                  = db_data['title']
      self.form['url_path'].data               = db_data['url_path']
      self.form['most_contribution'].data      = db_data['most_contribution']
      self.form['classification_type'].data    = db_data['classification_type']
      
      self.criterias = db_.select_query('criterias')
      self.criteria_id = db_data['criteria_id']

  def save(self):
    cp = self.form.data
    if self.form.data['upload_image'].filename:
      filename = './static/uploads/' + secure_filename(str(uuid.uuid1())+'.jpg')
      image_data = self.request.files['form-upload_image'].read()
      open(filename, 'wb').write(image_data)
      cp['url_path'] = filename[1:]

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
      msg, key = db_.delete(data)
      if key != -1:
        img_url = str(db_.select_query_by_id(self.key, 'images', 'image_id')['url_path'])
        if img_url.startswith('/static/uploads/'):
          os.remove('.'+img_url)
      return msg, key


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