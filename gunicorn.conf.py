import os

loglevel = 'info'
errorlog = f'{os.getcwd()}/logs/gunicorn_error.log'
accesslog = f'{os.getcwd()}/logs/gunicorn_access.log'
capture_output = True

# Number of worker processes
workers = 1

# The type of workers to use
worker_class = 'uvicorn.workers.UvicornWorker'

# The socket to bind
bind = 'unix:/home/ubuntu/tata-webhook/app.sock'

# Set umask for socket file
umask = 0o007
