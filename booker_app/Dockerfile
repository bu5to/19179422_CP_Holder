FROM python:3
WORKDIR /booker_app
ADD . /booker_app/booker_app

COPY booker_app.py /booker_app/booker_app.py
COPY static /booker_app/static/
COPY templates /booker_app/templates/


COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install pymongo

EXPOSE 5003

CMD ["python", "booker_app.py"]