#
# Gunicorn Config
# Used in the Docker container
#

bind = "0.0.0.0:8000"
workers = 4
daemon = True
wsgi_app = 'gtkserver:app'
