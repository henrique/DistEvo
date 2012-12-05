import webapp2
import logging

class MainPage(webapp2.RequestHandler):
  def get(self):
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Hello, webapp2 World!')
      
      
class Put(webapp2.RequestHandler):
  def put(self):
    logging.info('put received')
    name = self.request.body
    logging.info(name)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/put/', Put)],
                              debug=True)

logging.info('app startup?')