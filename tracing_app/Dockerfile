FROM python:3
WORKDIR /tracing_app
ADD . /tracing_app/tracing_app

COPY tracing_app.py /tracing_app/tracing_app.py
COPY models.py /tracing_app/models.py
COPY static /tracing_app/static/
COPY templates /tracing_app/templates/

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install pymongo

EXPOSE 5001

CMD ["python", "tracing_app.py"]