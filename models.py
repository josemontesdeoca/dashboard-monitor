# Copyright 2013 Jose Montes de Oca. All Rights Reserved.

"""Dashboard Monitor DB model classes."""

__author__ = 'Jose Montes de Oca <jfmontesdeoca11@gmail.com>'

from google.appengine.ext import ndb


class User(ndb.Model):
    """User Model.

    User model used with App Engine's User API.
    """

    user_id = ndb.StringProperty()
    email = ndb.StringProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True)


class Page(ndb.Model):
    """Models an specific page to be track."""

    METHODS = [
        'GET',
        'POST',
        'PUT',
        'HEAD',
        'DELETE',
    ]

    user = ndb.KeyProperty(kind=User)
    url = ndb.StringProperty()
    name = ndb.StringProperty()
    method = ndb.StringProperty(default='GET', choices=set(METHODS))
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    last_ping = ndb.DateTimeProperty()


class Ping(ndb.Model):
    """Models an specific ping action to a page."""
    page = ndb.KeyProperty(kind=Page)
    resp_time = ndb.IntegerProperty()
    resp_code = ndb.IntegerProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
