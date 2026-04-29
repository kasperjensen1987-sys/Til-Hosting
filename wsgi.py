from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app import app as exam_app
from cv_app import cv_app

# Dispatcher binder de to applikationer sammen uden at ændre app.py
application = DispatcherMiddleware(cv_app, {
    '/eksamen': exam_app
})

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, application, use_reloader=True, use_debugger=True)