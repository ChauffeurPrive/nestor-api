"""A valid WSGI file exporting an application that can be run by a server like gunicorn.
As described in https://wsgi.readthedocs.io/en/latest/what.html:
WSGI is the Web Server Gateway Interface. It is a specification that
describes how a web server communicates with web applications,
and how web applications can be chained together to process one request.
"""
from nestor_api.api.flask_app import create_app

app = create_app()
