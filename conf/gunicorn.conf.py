#
# Gunicorn Config
# Used in the Docker container
#

bind = "127.0.0.1:8000"
workers = 4
daemon = True
wsgi_app = 'gtkserver:app'
