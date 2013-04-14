# Copyright 2013 Jose Montes de Oca. All Rights Reserved.

"""Dashboard Monitor handlers."""

__author__ = 'Jose Montes de Oca <jfmontesdeoca11@gmail.com>'

from google.appengine.api import users
from webapp2_extras.appengine.users import login_required

import base
from models import User


class MainPageHandler(base.BaseHandler):
    """Main Page Handler serving '/' URIs."""
    def get(self):
        current_user = users.get_current_user()

        # Make sure a User entity gets created.
        if current_user:
            if not User.get_by_id(current_user.user_id()):
                self.redirect('/register')

        template_args = {
            'user': current_user,
            'login_url': users.create_login_url('/register'),
            'logout_url': users.create_logout_url('/')
        }

        self.render_template('index.html', **template_args)


class RegisterHandler(base.BaseHandler):
    """Register handler serving '/register'."""

    @login_required
    def get(self):
        current_user = users.get_current_user()

        user = User(id=current_user.user_id())
        user.user_id = current_user.user_id()
        user.email = current_user.email()

        user.put()

        self.redirect('/')
