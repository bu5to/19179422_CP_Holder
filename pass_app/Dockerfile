FROM python:3
WORKDIR /pass_app
ADD . /pass_app/pass_app

ARG DEBIAN_FRONTEND=noninteractive
ENV XDG_RUNTIME_DIR=/tmp

COPY models.py /pass_app/models.py
COPY pass_app.py /pass_app/pass_app.py
COPY static /pass_app/static/
COPY templates /pass_app/templates/

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install pymongo
RUN apt-get update
RUN apt-get install -y wkhtmltopdf

EXPOSE 5002

CMD ["python", "pass_app.py"]