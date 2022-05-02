FROM python:3
WORKDIR /user_account_app
ADD . /user_account_app/user_account_app

COPY user_account_app.py /user_account_app/user_account_app.py
COPY models.py /user_account_app/models.py
COPY static /user_account_app/static/
COPY templates /user_account_app/templates/


COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install pymongo

EXPOSE 5000

CMD ["python", "user_account_app.py"]