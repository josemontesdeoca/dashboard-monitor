# Copyright 2013 Jose Montes de Oca. All Rights Reserved.

"""Dashboard Monitor handlers."""

__author__ = 'Jose Montes de Oca <jfmontesdeoca11@gmail.com>'

import logging
import time
from webapp2_extras.appengine.users import login_required

from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.ext import ndb


import base
from models import User, Page, Ping


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
        except db.Error:
            self.redirect('/')


class MonitorHandler(base.BaseHandler):
    """Handler to dispatch monitor task to measure latency statistics."""
    def get(self):
        q = Page.query()

        logging.info('Starting Dispatch process')

        for page in q.iter():
            logging.info('Adding task to the queue to proccess '
                         '%s Web Page' % page.name)

            logging.info('urlsafe key %s' % page.key.urlsafe())
            taskqueue.add(url='/task/ping',
                          queue_name='ping',
                          params={'key': page.key.urlsafe()})


class PingHandler(base.BaseHandler):
    """Handler to ping web pages every five minutes.

    A cron job will call this handler every five minutes to record response
    times.
    """
    def post(self):
        key = ndb.Key(urlsafe=self.request.get('key'))

        page = key.get()

        if page:
            start_time = time.time()

            result = urlfetch.fetch(url=page.url,
                                    deadline=30,
                                    headers={'Cache-Control': 'max-age=0'})

            resp_time = int((time.time() - start_time) * 1000)

            logging.info('fetching %s - response time: %d ms'
                         % (page.url, resp_time))

            ping = Ping()
            ping.page = page.key
            ping.resp_time = resp_time
            ping.resp_code = result.status_code
            ping.put()
        else:
            logging.error('ERROR retrieving page to be monitored.')
