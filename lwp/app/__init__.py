#!/usr/bin/env python
# encoding: utf-8
import flask
import os

# Flask app
TEMPLATE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'))
print TEMPLATE_PATH
app = flask.Flask('lwp', template_folder=TEMPLATE_PATH)
app.config.from_object('lwp')

from views import *
