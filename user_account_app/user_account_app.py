from flask import Flask, request, render_template, url_for, redirect, session
try:
    from user_account_app.models import User, Trace, Crownpass
except:
    from models import User, Trace, Crownpass
import base64
import pymongo
import os

myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Through this URL, the user will register. Notice that
    the photo uploaded by the user will be converted to a Base64 string,
    in order not to store the file anywhere.
    As for the rest of the inputs, the user will be saved in the database
    given the inputs below (Infection status, vaccination status, phone, e-mail...)
    :return: The page where the user will register.
    '''
    if request.method == 'POST':
        mydb = myclient["users"]
        mycol = mydb["users"]
        crownpassid = len(list(mycol.find())) + 1
        print(request.files)
        if 'file' not in request.files:
            staticfolder = app.static_folder
            print(staticfolder)
            photoFile = open(staticfolder + "/images/testuser.jpg", "rb")
            photo = base64.b64encode(photoFile.read())
        else:
            photoFile = request.files.get('file')
            photo = base64.b64encode(photoFile.read())
        qr = "/qr" + str(crownpassid)
        infStatus = request.form['infStatus']
        print(infStatus)
        vacStatus = request.form['vacStatus']
        print(vacStatus)
        phone = request.form['phone']
        print(phone)
        email = request.form['email']
        print(email)
        home = request.form['home']
        print(home)
        name = request.form['name']
        print(name)
        gender = request.form['gender']
        birthdate = request.form['birthdate']
        user = User(crownpassid, photo, qr, phone, email, home, name, gender, birthdate)
        crownpass = Crownpass(crownpassid, infStatus, vacStatus)
        userDict = User.parseToDict(user)
        x = mycol.insert_one(userDict)
        mydb = myclient["crownpass"]
        mycol = mydb["crownpass"]
        passDict = Crownpass.parseToDict(crownpass)
        x = mycol.insert_one(passDict)

        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Through this URL, the user will log in. The user will not need to introduce any password,
    as the system does not require any passwords.
    :return: The login page.
    '''
    if request.method == 'POST':
        user = User.get_by_id(request.form['crownpassid'])
        if user is not None:
            session['user'] = user.crownpassid
            return redirect(url_for('index'))
        else:
            flash("This user does not exist.")
    return render_template('login.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    '''
    Lets the user refresh the settings of the user and, also, clean his movement tracing
    history.
    :return: The account settings page.
    '''
    user = User.get_by_id(session['user'])
    if request.method == "POST":
        filter = {'crownpassid': session['user']}
        newvalues = {"$set": {'phone': request.form['phone'],
                              'email': request.form['email'],
                              'gender': request.form['gender'],
                              'home': request.form['home'],
                              }}
        mydb = myclient["users"]
        mycol = mydb["users"]
        mycol.update_one(filter, newvalues)
    userdict = User.get_by_id(session["user"]).parseToDict()
    userdict.pop('photo')
    print("New user details:")
    print(userdict)

    return render_template("account-settings.html", user=user)


@app.route('/wipetracing')
def wipetracing():
    '''
    This URL resets the tracing history from a user, removing every row.
    :return: Redirect to "account settings".
    '''
    Trace.wipeTracing(session['user'])
    return redirect(url_for('settings'))


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
