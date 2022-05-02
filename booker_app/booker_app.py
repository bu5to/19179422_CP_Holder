from flask import Flask, request, render_template, session
import os
import pymongo

myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == "POST":
        vacCentre = request.form['vacCentre']
        user = session['user']
        strDate = request.form['date']
        strType = request.form['vacType']
        mydb = myclient["vaccination"]
        mycol = mydb["vaccination"]
        strDict = {
            "vacCentre": vacCentre,
            "user": user,
            "date": strDate,
            "vacType": strType,
        }
        mycol.insert_one(strDict)

    return render_template("book-vaccination.html")


@app.route('/booktest', methods=['GET', 'POST'])
def booktest():
    if request.method == "POST":
        testCentre = request.form['testcentre']
        user = session['user']
        strDate = str(request.form['date']) + " " + request.form["hour"] + ":" + request.form["minutes"]
        testtype = request.form["testtype"]
        mydb = myclient["tests"]
        mycol = mydb["tests"]
        strDict = {
            "testCentre": testCentre,
            "user": user,
            "date": strDate,
            "type": testtype,
            "result": "Not given"
        }
        mycol.insert_one(strDict)

    return render_template("book-test.html")


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
