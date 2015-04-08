import time

from unittest import TestCase
from flask import Flask

from apianalytics.middleware import FlaskMiddleware
from tests.helpers import host, zmq_pull_once


##
# Test Flask middleware
##
class FlaskMiddewareTest(TestCase):

  def setUp(self):
    self.app = Flask('test')
    self.app.wsgi_app = FlaskMiddleware(self.app.wsgi_app, 'SERVICE-TOKEN', host())

    self.client = self.app.test_client()

    @self.app.route('/get')
    def show_get():
      return 'Hello World'

    @self.app.route('/post', methods=['POST'])
    def show_post():
      return 'Hello World'

  @property
  def middleware(self):
    return self._middleware

  def test_get(self):
    recv = self.client.get('/get?foo=bar', headers={'CONTENT_TYPE': 'text/plain', 'X-Custom': 'custom'})
    time.sleep(0.1)  # Sleep for 10 ms

    self.assertIn('200 OK', recv.status)
    self.assertIn('Hello', recv.data)

    json = zmq_pull_once(host())

    self.assertTrue(json['har']['log']['entries'][0]['timings']['wait'] >= 10)


  def test_post(self):
    recv = self.client.post('/post', data='post data')
    time.sleep(0.01)  # Sleep for 10 ms

    self.assertIn('200 OK', recv.status)
    self.assertIn('Hello', recv.data)

    json = zmq_pull_once(host())

    self.assertTrue(json['har']['log']['entries'][0]['timings']['wait'] >= 10)
