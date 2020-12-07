from flask import Flask, render_template
from flask_login import LoginManager

import views
from user import get_user

lm = LoginManager()

@lm.user_loader
def load_user(user_id):
  return get_user(user_id)


def create_app():
  app = Flask(__name__)
  app.config.from_object("settings")
  app.add_url_rule("/", view_func=views.home_page)
  app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
  app.add_url_rule("/logout", view_func=views.logout_page)

  lm.init_app(app)
  lm.login_view = "login_page"
  
  return app

if __name__ == "__main__":
  app = create_app()
  port = app.config.get("PORT", 5000)
  app.run("127.0.0.1", port=port)