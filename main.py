# Copyright 2013 Jose Montes de Oca. All Rights Reserved.

"""Application Main entry point."""

__author__ = 'Jose Montes de Oca <jfmontesdeoca11@gmail.com>'

import os
import webapp2

import handlers

DEBUG = os.getenv('SERVER_SOFTWARE', '').startswith('Dev')


application = webapp2.WSGIApplication([
    ('/', handlers.MainPageHandler),
    ('/register', handlers.RegisterHandler),
    ('/new-page', handlers.NewPageHandler),
    ('/cron/monitor', handlers.MonitorHandler),
    ('/task/ping', handlers.PingHandler),
    ('/monitor.json', handlers.VisualizeHandler),
    ('/viz/v1/dailyLatency/page/(\w+)', handlers.DailyLatencyVizHandler),
    ('/page/(\w+)', handlers.DashboardHandler),
], debug=DEBUG)
