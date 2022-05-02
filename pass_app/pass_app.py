from flask import Flask, render_template, url_for, send_file, session, Response, request, flash
try:
    from pass_app.models import User, Crownpass
except:
    from models import User, Crownpass

import datetime
import os
import requests
import io
import pdfkit
import html
import pymongo
import qrcode
import base64

myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
try:
    # path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
except:
    pass


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/photo/<int:crownpassid>')
def photo(crownpassid):
    '''
    The users' pictures are saved as a Base64 encoded string in order to
    avoid occupying storage in the project folder.
    In this method, the string is decoded and the image is displayed as
    the content of the response. The result of the decoded string is an array of bytes.
    :param crownpassid: The ID of the user whose picture is displayed.
    :return: The image as an array of bytes.
    '''
    user = User.get_by_id(crownpassid)
    image_64_decode = base64.b64decode(user.photo)
    return Response(image_64_decode, mimetype='image/jpg')


@app.route('/crownpass/<int:crownpassid>', methods=['GET', 'POST'])
def crownpass(crownpassid):
    '''
        This URL leads the Crownpass user to see all his pass details.
        :param crownpassid: The ID of the Crownpass user.
        :return: A page with all the details of the Crownpass holder.
    '''
    user = User.get_by_id(crownpassid)
    cp = Crownpass.get_by_id(crownpassid)
    # session['user'] = crownpassid
    if session.get('user'):
        if user.crownpassid == session['user']:
            return render_template("pass.html", user=user, crownpass=cp)
        else:
            return "You are not allowed to check out other users' passes.", 500
    else:
        return "You are not logged in.", 500


@app.route('/genpass/<int:crownpassid>')
def genpass(crownpassid):
    '''
        This URL generates a Crownpass to be printed.
        :param crownpassid: The ID of the Crownpass user.
        :return: A page with all the details of the Crownpass holder.
    '''
    user = User.get_by_id(crownpassid)
    cp = Crownpass.get_by_id(crownpassid)
    return render_template("genpass.html", user=user, crownpass=cp)


@app.route('/print/<int:crownpassid>')
def printpass(crownpassid):
    '''
    A method that converts the URL that shows the Crownpass details to PDF
    and returns the created PDF document as a file.
    There is no universal method to print the document from Python.
    The method varies depending on the platform. This is why it has been decided to
    include a PDF.
    To convert the file to PDF, an external service is called, namely WKHtmlToPDF.
    :param crownpassid: The ID of the Crownpass user.
    :return: A PDF file with the details of the Crownpass.
    '''
    options = {
        "enable-local-file-access": None
    }
    # Convert HTML file to PDF and see the output as response. Don't print.
    url = url_for("genpass", crownpassid=str(crownpassid), _external=True)
    r = requests.get(url)
    pdfkit.from_string(html.unescape(r.text), 'out.pdf', options=options)
    return send_file('out.pdf', attachment_filename='pass.pdf')


@app.route('/qr/<int:crownpassid>')
def qr(crownpassid):
    '''
    This method creates, using the QRCode library, a QR that the holder
    will use to be authorized to enter controlled areas. This QR code is returned
    as a PNG file.
    :param crownpassid: The ID of the user whose QR is displayed.
    :return: The QR is displayed.
    '''
    img = qrcode.make(url_for('authorize', crownpassid=crownpassid, _external=True))
    with io.BytesIO() as output:
        img.save(output, format="PNG")
        contents = output.getvalue()
    return Response(contents, mimetype='image/png')


@app.route('/authorize/<int:crownpassid>', methods=['GET', 'POST'])
def authorize(crownpassid):
    '''
        A method that authorizes the user to enter a place if the user
        is vaccinated. A timestamp along with the ID of the user who has requested
        authorization are recorded in the database.
        :param crownpassid: The ID of the Crownpass user.
        :return: Returns a string stating if the user has been authorized or not.
    '''
    mydb = myclient["controlledAreas"]
    mycol = mydb["controlledAreas"]
    x = mycol.find()
    listDict = list(x)
    areas = []
    for element in listDict:
        areas.append(element['name'])
    if request.method == "POST":
        date = datetime.datetime.now()
        strDate = date.strftime("%Y/%m/%d, %H:%M:%S")
        strDict = {
            "crownpassid": crownpassid,
            "date": strDate,
            "area": request.form["area"],
            "check": request.form["check"]
        }
        mydb = myclient["tracing"]
        mycol = mydb["tracing"]
        x = mycol.insert_one(strDict)
        return redirect(url_for('index'))  # Change this by a string containing the response.
    return render_template('checkin.html', areas=areas, crownpassid=crownpassid)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
