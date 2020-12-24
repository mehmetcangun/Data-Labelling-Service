from flask import Flask, render_template
from flask_login import LoginManager

import views
from user import get_user

lm = LoginManager()

@lm.user_loader
def load_user(user_id):
  return get_user(user_id)

app = Flask(__name__)

app.config.from_object("settings")
app.add_url_rule("/", view_func=views.home_page)

# users....
app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
app.add_url_rule("/logout", view_func=views.logout_page)
app.add_url_rule("/register_admin", view_func=views.register_page, methods=['GET', 'POST'])
app.add_url_rule("/register_labeller", view_func=views.register_page, methods=['GET', 'POST'])

app.add_url_rule("/domains", view_func=views.domain_index_page, methods=['GET'])
app.add_url_rule("/domains_add", view_func=views.domain_add_page, methods=['GET', 'POST'])
app.add_url_rule("/domains_update/<int:key>", view_func=views.domain_update_page, methods=['GET', 'POST'])
app.add_url_rule("/domains_delete/<int:key>", view_func=views.domain_delete_page, methods=['GET', 'POST'])
app.add_url_rule("/domains_details/<int:key>", view_func=views.domains_details_page, methods=['GET'])

app.add_url_rule("/subdomains", view_func=views.subdomain_index_page, methods=['GET', 'POST'])
app.add_url_rule("/subdomains_add/<int:domain_id>", view_func=views.subdomain_add_page, methods=['GET', 'POST'])
app.add_url_rule("/subdomains_details/<int:key>", view_func=views.subdomains_details_page, methods=['GET'])
app.add_url_rule("/subdomains_update/<int:key>", view_func=views.subdomain_update_page, methods=['GET', 'POST'])
app.add_url_rule("/subdomains_delete/<int:key>", view_func=views.subdomain_delete_page, methods=['GET', 'POST'])

'''
app.add_url_rule("/users")
app.add_url_rule("/profile/<int:user_key>")
app.add_url_rule("/contributions/<int:user_key>")
app.add_url_rule("/delete_my_account")

# images...
app.add_url_rule("/images")
app.add_url_rule("/image_add/<int:criteria_key>")
app.add_url_rule("/image_update/<int:image_key>")
app.add_url_rule("/image_details/<int:image_key>")
app.add_url_rule("/image_delete/<int:image_key>")


# subdomains...
app.add_url_rule("/subdomains")
app.add_url_rule("/subdomain_add/<int:domain_key>")
app.add_url_rule("/subdomain_details/<int:subdomain_key>")
app.add_url_rule("/subdomain_update/<int:subdomain_key>")
app.add_url_rule("/subdomain_delete/<int:subdomain_key>")

# criterias...
app.add_url_rule("/criterias")
app.add_url_rule("/criteria_add")
app.add_url_rule("/criteria_details/<int:criteria_key>")
app.add_url_rule("/criteria_update/<int:criteria_key>")
app.add_url_rule("/criteria_delete/<int:criteria_key>")
'''


lm.init_app(app)
lm.login_view = "login_page"

def page_not_found(e):
  return render_template('page-404.html'), 404

def page_no_authorization(e):
  return render_template('page-403.html'), 403

app.register_error_handler(404, page_not_found)
app.register_error_handler(403, page_no_authorization)

if __name__ == "__main__":
  app = create_app()
  port = app.config.get("PORT", 5000)
  app.run("127.0.0.1", port=port)