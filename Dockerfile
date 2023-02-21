FROM python:3.10

WORKDIR /app

ADD . /app
RUN pip install  -r requirements.txt && mkdir "/var/log/uwsgi"

CMD ["uwsgi","uwsgi.ini"]