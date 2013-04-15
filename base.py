# Copyright 2013 Jose Montes de Oca. All Rights Reserved.

"""Base Handlers."""

__author__ = 'Jose Montes de Oca <jfmontesdeoca11@gmail.com>'

import os
import jinja2
import webapp2

from google.appengine.api import users


class BaseHandler(webapp2.RequestHandler):
    """Base Handler.

    Base handler which provides useful methods to render the response.
    """
    @webapp2.cached_property
    def jinja_environment(self):
        return jinja2.Environment(loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), 'templates')))

    def render_template(self, filename, **kwargs):
        """Render a jinja2 template from webapp2 micro framework.

        Args:
            filename: template name
            kwargs: dict tor jinja templates
        """

        kwargs.update({
            'user': users.get_current_user(),
            'login_url': users.create_login_url('/register'),
            'logout_url': users.create_logout_url('/')
        })

        template = self.jinja_environment.get_template(filename)
        self.response.out.write(template.render(**kwargs))
