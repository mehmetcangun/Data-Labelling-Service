from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, BooleanField, FormField, SubmitField, TextAreaField, RadioField, FileField
from wtforms.validators import DataRequired, EqualTo, Length, Optional
from wtforms.fields.html5 import EmailField, DecimalRangeField, URLField
from wtforms_components import IntegerField, ColorField

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


class Domain(FlaskForm):
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
class DomainForm(FlaskForm):
  
  form = FormField(Domain)
  submit  = SubmitField( render_kw = { "class" : "btn-primary"})
  
  key = None
  def init_key(self, **keys):
    self.key = keys['key']
    
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


class Subdomain(FlaskForm):
  name = StringField("name", validators=[DataRequired()])
  priority_rate = RadioField(
    "Priority Rate(10 higher rate than 1)",
    default = 1,
    coerce=int,
    choices = [ x for x in range(1, 11) ],
    render_kw = { "class" : "list-group list-group-horizontal" }
  )
  icon = StringField("icon", validators=[Optional()])

class SubdomainForm(FlaskForm):
  form = FormField(Subdomain)
  submit  = SubmitField( render_kw = { "class" : "btn-primary"})

  key = None
  FKDomainId = None
  
  def init_key(self, **keys):
    self.key = keys['key']
    self.FKDomainId = keys['FK']

    if self.key is not None:
      subdomain = Database()
      print(self.key)
      subdomains = subdomain.select_query_by_id(self.key, 'subdomains', 'subdomain_id')
      print(subdomains)
      self.form['name'].data           = subdomains['name']
      self.form['priority_rate'].data  = subdomains['priority_rate']
      self.form['icon'].data           = subdomains['icon']
  
  
  def save(self):
    cp = self.form.data
    cp.pop('csrf_token', None)
    if self.FKDomainId is not None:
      for i in self.FKDomainId:
        cp[i[0]] = i[1]
    print(cp)
    data = {
      'primary_key': 'subdomain_id',
      'table_name': 'subdomains',
      'data': cp,
      'where': {
        'subdomain_id': self.key
      }
    }
    subdomain_db = Database()
    if self.key is None:
      return subdomain_db.add(data)
    return subdomain_db.update(data)

def criteria_selection(form, field):
  if form.data < -5.0 and form.data > 5:
    raise ValidationError("Must be between -5.0 and 5.0")

class Criterias(FlaskForm):
  for_contribution = DecimalRangeField("For Contribution", validators=[criteria_selection])
  correctness = DecimalRangeField("Correctness", validators=[criteria_selection])
  wrongness = DecimalRangeField("Wrongness", validators=[criteria_selection])
  reported = DecimalRangeField("Reported", validators=[criteria_selection])
  extra_info = DecimalRangeField("Extra Information", validators=[criteria_selection])

class Images(FlaskForm):
  title = StringField("title", validators=[DataRequired()])
  url_path = URLField("Image Url")
  upload_image = FileField('Image File', )
  most_contribution = IntegerField("Most Contribution(by labeller)", min=1)
  classification_type = SelectField(
    "Classification Type",
    choices = [("Binary Classification", "Binary Classification"), ("Multi-Class", "Multi-Class"), ("Multi-Label","Multi-Label")],
    render_kw = { "class" : "form-control"}
  )

class Labels(FlaskForm):
  is_correct = BooleanField("Correct")

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