import sys
from flask_mail import Mail, Message
from flask import Flask, request, render_template
import datetime

try:
    from tracing_app.models import User, Trace, CovidTest, Vaccine
except:
    from models import User, Trace, CovidTest, Vaccine
import os
import pymongo

myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


@app.route('/showtrace/<int:crownpassid>', methods=['GET', 'POST'])
def showtrace(crownpassid):
    '''
        This URL shows the trace of the user given his crownpassid.
        Moreover, there is an extra feature that shows the trace of the user
        given certain dates.
        :param crownpassid: The ID of the Crownpass user.
        :return: A page with the trace of the Crownpass holder.
    '''
    user_trace = list(Trace.get_by_id(crownpassid))
    orderedByDate = []
    traceArray = []
    covidTests = list(CovidTest.get_by_id(crownpassid))
    print(covidTests)
    vaccines = list(Vaccine.get_by_id(crownpassid))

    if request.method == "POST":
        startDate = datetime.datetime.strptime(request.form['start'], "%Y-%m-%d")
        endDate = datetime.datetime.strptime(request.form['end'], "%Y-%m-%d") + datetime.timedelta(days=1)
        for x in user_trace:
            date = datetime.datetime.strptime(x['date'], "%Y/%m/%d, %H:%M:%S")
            orderedByDate.append((x['crownpassid'], date, x['area'], x['check']))
        for y in orderedByDate:
            if y[1] >= startDate and y[1] <= endDate:
                traceArray.append(Trace(y[0], y[1].strftime("%Y/%m/%d, %H:%M:%S"), y[2], y[3]))
        for z in traceArray:
            print(z.__dict__)
        # return redirect(url_for('showtrace', tracing=traceArray, crownpassid=crownpassid))
    #    return render_template("tracing.html", tracing=traceArray, crownpassid = crownpassid)
    else:
        for x in user_trace:
            x['date'] = datetime.datetime.strptime(x['date'], "%Y/%m/%d, %H:%M:%S")
            orderedByDate.append((x['crownpassid'], x['date'], x['area'], x['check']))
            orderedByDate = sorted(orderedByDate)
        for z in orderedByDate:
            traceArray.append(Trace(z[0], str(z[1].strftime("%Y/%m/%d, %H:%M:%S")), z[2], z[3]))
    return render_template("check-trace.html", tracing=traceArray, crownpassid=crownpassid, vaccines=vaccines,
                           covidTests=covidTests)


@app.route('/notifyPositiveTest/<int:crownpassid>')
def notifyPositiveTest(crownpassid):
    '''
    The user is searched given its Crownpass ID, and an email is written to that user to
    report the test as positive.
    :param crownpassid: The ID of the user whose tested is reported as positive.
    :return: A string stating that the message has been sent.
    '''
    user = User.get_by_id(crownpassid)
    mail = Mail(app)
    msg = Message(sender=("Jorge from Crownpass", 'soft7011cwk2jb@gmail.com'), recipients=[user.email],
                  subject="COVID-19 Test: Report")
    msg.html = "Dear " + user.name + ",<br> hereby we confirm that your COVID-19 test has been returned as " \
                                     "<b>positive.</b> Do not forget to stay isolated and comply with the " \
                                     "required regulations. The Crownpass team wishes you a safe recovery." \
                                     "<br> Yours sincerely, <br> the <b>Crownpass</b> team."
    mail.send(msg)
    return "Message sent."


@app.route('/tracing/<int:crownpassid>', methods=['GET', 'POST'])
def tracing(crownpassid):
    '''
        This URL shows the trace of the user given his crownpassid.
        Moreover, there is an extra feature that shows the trace of the user
        given certain dates.
        :param crownpassid: The ID of the Crownpass user.
        :return: A page with the trace of the Crownpass holder.
    '''
    user_trace = list(Trace.get_by_id(crownpassid))
    orderedByDate = []
    traceArray = []

    if request.method == "POST":
        startDate = datetime.datetime.strptime(request.form['start'], "%Y-%m-%d")
        endDate = datetime.datetime.strptime(request.form['end'], "%Y-%m-%d") + datetime.timedelta(days=1)
        for x in user_trace:
            date = datetime.datetime.strptime(x['date'], "%Y/%m/%d, %H:%M:%S")
            orderedByDate.append((x['crownpassid'], date, x['area'], x['check']))
        for y in orderedByDate:
            if y[1] >= startDate and y[1] <= endDate:
                traceArray.append(Trace(y[0], y[1].strftime("%Y/%m/%d, %H:%M:%S"), y[2], y[3]))
        for z in traceArray:
            print(z.__dict__)
    else:
        for x in user_trace:
            x['date'] = datetime.datetime.strptime(x['date'], "%Y/%m/%d, %H:%M:%S")
            orderedByDate.append((x['crownpassid'], x['date'], x['area'], x['check']))
            orderedByDate = sorted(orderedByDate)
        for z in orderedByDate:
            traceArray.append(Trace(z[0], str(z[1].strftime("%Y/%m/%d, %H:%M:%S")), z[2], z[3]))
    return render_template("tracing.html", tracing=traceArray, crownpassid=crownpassid)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
