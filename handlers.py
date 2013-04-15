# Copyright 2013 Jose Montes de Oca. All Rights Reserved.

"""Dashboard Monitor handlers."""

__author__ = 'Jose Montes de Oca <jfmontesdeoca11@gmail.com>'

from google.appengine.api import users
from webapp2_extras.appengine.users import login_required

import base
from models import User
from models import Page


class MainPageHandler(base.BaseHandler):
    """Main Page Handler serving '/' URIs."""
    def get(self):
        current_user = users.get_current_user()

        template_args = {}

        # Make sure a User entity gets created.
        if current_user:
            user = User.get_by_id(current_user.user_id())
            if not user:
                self.redirect('/register')
            else:
                q = Page.query(ancestor=user.key)
                q = q.order(Page.name)

                pages = q.fetch(10)

                template_args.update({
                    'pages': pages,
                })

        self.render_template('index.html', **template_args)


class RegisterHandler(base.BaseHandler):
    """Register handler serving '/register'."""

    @login_required
    def get(self):
        current_user = users.get_current_user()

        if not User.get_by_id(current_user.user_id()):
            user = User(id=current_user.user_id())
            user.user_id = current_user.user_id()
            user.email = current_user.email()

            user.put()

        self.redirect('/')


class NewPageHandler(base.BaseHandler):
    """New page handler serving '/new-page'."""

    @login_required
    def get(self):
        self.render_template('new-page.html')

    def post(self):
        current_user = users.get_current_user()

        if not current_user:
            return self.redirect('/')

        user = User.get_by_id(current_user.user_id())

        if not user:
            return self.redirect('/register')

        try:
            page = Page(parent=user.key)
            page.user = user.key
            page.url = self.request.get('url')
            page.name = self.request.get('name')
            page.put()

            self.redirect('/')
        except db.Error, e:
            self.redirect('/')
