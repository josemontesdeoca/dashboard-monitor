# Copyright 2013 Jose Montes de Oca. All Rights Reserved.

"""Dashboard Monitor handlers."""

__author__ = 'Jose Montes de Oca <jfmontesdeoca11@gmail.com>'

import logging
import time
from datetime import datetime
from webapp2_extras.appengine.users import login_required

from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.ext import ndb


import base
from lib import gviz_api
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

                # Issue asynchronous fetch operations per page
                for page in pages:
                    query = Ping.query(Ping.page == page.key)
                    query = query.order(-Ping.date)

                    # fetch 288 pings representing the last 24 hrs
                    page.pings_future = query.fetch_async(288)

                # Reading fetch results and calculate avg latency
                for page in pages:
                    pings = page.pings_future.get_result()

                    total_resp_time = 0

                    if pings:
                        for p in pings:
                            total_resp_time += p.resp_time

                        page.avg_resp_time = total_resp_time/len(pings)

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
            try:
                start_time = time.time()

                result = urlfetch.fetch(url=page.url,
                                        deadline=30,
                                        headers={'Cache-Control': 'max-age=0'})

                resp_time = int((time.time() - start_time) * 1000)

                logging.info('fetching %s - response time: %d ms'
                             % (page.url, resp_time))

                @ndb.transactional(xg=True)
                def save_ping():
                    ping = Ping()
                    ping.page = page.key
                    ping.resp_time = resp_time
                    ping.resp_code = result.status_code
                    ping.put()

                    # Update Last Ping data
                    page.last_ping = datetime.now()
                    page.put()

                save_ping()

            except urlfetch.DownloadError as e:
                logging.error('Error: %s' % e)
            except urlfetch.ResponseTooLargeError as e:
                logging.error(e)
            except urlfetch.InvalidURLError as e:
                logging.error("Invalid URL '%s' \n %s" % (page.url, e))
            except urlfetch.Error as e:
                logging.error(e)
        else:
            logging.error('ERROR retrieving page to be monitored.')


class VisualizeHandler(base.BaseHandler):
    """Handler to generate a DataTable for visualization."""

    @login_required
    def get(self):

        try:
            key = ndb.Key(urlsafe=self.request.get('page'))
            page = key.get()
        except:
            logging.error('Error generating Page object from urlsafe string.')
            page = None

        user = User.get_by_id(users.get_current_user().user_id())

        if page:
            if page.user == user.key:
                description = {
                    'date': ('datetime', 'Fecha'),
                    'resp_time': ('number', 'Tiempo de respuesta'),
                }

                data = []

                # Query the data
                query = Ping.query(Ping.page == page.key)
                query = query.order(-Ping.date)

                # fetch 288 pings representing the last 24 hrs
                pings = query.fetch(288)

                for ping in pings:
                    entry = {
                        'date': ping.date,
                        'resp_time': ping.resp_time,
                    }
                    data.append(entry)

                data_table = gviz_api.DataTable(description)
                data_table.LoadData(data)

                self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write(data_table.ToJSonResponse(
                    columns_order=('date', 'resp_time'),
                    order_by="date"))
            else:
                # Return 401 Unauthorized
                logging.error('Unauthorized')
                self.response.set_status(401)
                self.response.out.write('Unauthorized')
        else:
            # Return 404 Not Found
            logging.error('Not Found')
            self.response.set_status(404)
            self.response.out.write('Not Found')


class DashboardHandler(base.BaseHandler):
    @login_required
    def get(self, urlsafe_key):
        user = User.get_by_id(users.get_current_user().user_id())

        try:
            logging.info('Get page by urlsafe %s' % urlsafe_key)

            key = ndb.Key(urlsafe=urlsafe_key)
            page = key.get()
        except:
            logging.error('Error generating Page object from key.id().')
            page = None

        if page:
            if page.user == user.key:
                template_args = {
                    'page': page,
                }

                self.render_template('dashboard.html', **template_args)
            else:
                # Return 401 Unauthorized
                self.response.set_status(401)
                self.response.out.write('Unauthorized')
        else:
            # Return 404 Not Found
            self.response.set_status(404)
            self.response.out.write('Not Found')
