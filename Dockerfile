FROM python:3.6

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

WORKDIR /app/

# -- Installing pipenv
RUN pip install --upgrade pip
RUN pip install pipenv

# -- Adding Pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# -- Install dependencies:
RUN pipenv install --deploy --system

COPY . /app

CMD ["python", "nestor_api/api/wsgi.py"]