import os

loglevel = 'info'
errorlog = f'{os.getcwd()}/logs/gunicorn_error.log'
accesslog = f'{os.getcwd()}/logs/gunicorn_access.log'
capture_output = True

workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Bind to TCP for Docker networking
bind = '0.0.0.0:8000'
