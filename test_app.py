import sys
import os
import pytest
from booker_app.booker_app import app as bookerApp
from user_account_app.user_account_app import app as userAccApp
from pass_app.pass_app import app as passApp
from tracing_app.tracing_app import app as tracingApp
from tracing_app.models import CovidTest, Vaccine
import pymongo
import time


@pytest.fixture
def clientBooker():
    bookerApp.secret_key = 'thisisasecretkey'
    clientBooker = bookerApp.test_client()
    with clientBooker.session_transaction(subdomain='blue') as session:
        session['user'] = 1
    return clientBooker


@pytest.fixture
def clientUser():
    userAccApp.secret_key = 'thisisasecretkey'
    clientUser = userAccApp.test_client()
    return clientUser


@pytest.fixture
def clientTrace():
    clientTrace = tracingApp.test_client()
    return clientTrace


@pytest.fixture
def clientPass():
    clientPass = passApp.test_client()
    return clientPass


def test_crownpassReg(clientUser):
    '''
    QR-PF-01: Registration of Crownpass.
    The response time for each interactive operation in the process of registration
    for a Crownpass should be no more than 20 seconds.
    '''
    start = time.time()
    response = clientUser.post("/register", data={
        "name": "Sample testing user",
        "infStatus": "No infection",
        "vacStatus": "Two or more doses",
        "phone": "000011112222",
        "email": "sampleuser@brookes.ac.uk",
        "home": "Home address",
        "birthdate": "1999/01/01",
        "gender": "Male",
        "photo": open('user_account_app/static/images/testuser.jpg', 'rb')
    },follow_redirects=True)
    end = time.time() #The timestamp is recorded after processing the POST request.
    myclient = pymongo.MongoClient("mongodb+srv://19179422:soft7011@cluster0.whl83.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    mydb = myclient["users"]
    mycol = mydb["users"]
    myquery = {"name": "Sample testing user"}
    mycol.delete_one(myquery) #The registered user is deleted after having created it.
    assert ((end - start) < 20 and response.status_code == 200)


def test_checkInCheckOut(clientTrace):
    '''
    QR-PF-02: Check-in.
    The response time for check-in a Crownpass holder into a controlled area should be no more than 3 seconds.
    QR-PF-03: Check-out.
    The response time for check-out a Crownpass holder out of a controlled area should be no more than 10 seconds.
    '''
    start = time.time()
    response = clientTrace.get("/showtrace/1",follow_redirects=True)
    end = time.time()
    assert ((end - start) < 3 and response.status_code == 200)


def test_changePassRed(clientTrace):
    '''
    QR-PF-04: Change Pass State to Red.
    The time that a Crownpass’ state is changed into RED should be no more than 1
    second after the Crownpass holder’s virus test result being positive is entered into the system.
    QR-PF-07: Notification of State Change.
    The notification of the state change to a Crownpass holder should be sent out within 10 seconds after the state
    change takes place, if the notification is required.
    Here, both quality requirements are combined and the time is measured.
    '''
    start = time.time()
    CovidTest.setColor("red", 1)
    response = clientTrace.get("/notifyPositiveTest/1",follow_redirects=True)
    end = time.time()
    assert ((end - start) < 11 and response.status_code == 200)


def test_changePassAmber():
    '''
    QR-PF-05: Change Pass State to Amber.
    The time that a Crownpass’ state is changed into Amber should be no more than
    5 seconds after a Crownpass holder’s virus test result being positive entered into the system.
    '''
    start = time.time()
    CovidTest.setColor("amber", 1)
    end = time.time()
    assert ((end - start) < 5)


def test_changePassGreen():
    '''
    QR-PF-06: Change Pass State to Green
    The time that a Crownpass’ state is changed into Green should be no more than 5 seconds
    after the pass holder’s virus test result being negative is entered into the system.
    '''
    start = time.time()
    CovidTest.setColor("green", 1)
    end = time.time()
    assert ((end - start) < 5)


def test_privacy(clientPass, clientUser):
    '''
    QR-SE-01: Individual User Data Privacy Protection.
    The following elements of a Crownpass holder’s data are private and can only be accessed
    for viewing by the user of the Crownpass holder.
    Name and address, contact details, and user tracing.
    '''
    response = clientPass.get("/crownpass/1")
    print(response)
    assert (response.status_code == 500) #An error is thrown if a user tries to check a pass without having logged in or if the pass does not belong to him.


def raisingError(response):
    '''
    Method used to raise a KeyError if the user is missing.
    :param response: the request made to the client to access the user's data.
    :return: OK if no error is thrown, KeyError if there is an error (which will be)
    '''
    if response.status_code == 500:
        raise KeyError("user")
    else:
        return 200


def test_modifyData(clientUser):
    '''
    QR-SE-01: Individual User Data Privacy Protection.
    The following elements of a Crownpass holder’s data are private and can only be accessed
    for modification by the user of the Crownpass holder.
    Name and address, contact details, and user tracing.
    '''
    response = clientUser.get("/wipetracing") #By the structure of the wipetracing() method, it is impossible to reset the movement trace of another user.
    with pytest.raises(KeyError):
        assert raisingError(response) #However, it is made sure that the movement trace cannot be reset from a non logged-in user.


def test_loginOK(clientUser):
    '''
    Logging in attempt with a user that already exists.
    :return: Response 200. The user exists.
    '''
    response = clientUser.post("/login", data={
        "crownpassid": "1"
    },follow_redirects=True)
    assert (response.status_code == 200)


def test_loginError(clientUser):
    '''
    Logging in attempt with a user that does not exist.
    :return: Response 500. The user does not exist.
    '''
    response = clientUser.post("/login", data={
        "crownpassid": "2398983489342938"
    },follow_redirects=True)
    assert (response.status_code == 500)


def test_bookCovidTest(clientBooker):
    '''
    Test ran to verify that the COVID-19 tests can be successfully booked.
    The length of the tests table of the database is measured before and
    after the POST request.
    :return: Response 200 for the POST request, and an assertion that
    verifies that the array of tests for that user is larger than before.
    '''
    crownpassid = 1
    covidTests = list(CovidTest.get_by_id(crownpassid))
    lengthBefore = len(covidTests)
    response = clientBooker.post("/booktest", data={
        "testcentre": "Sample Testing Centre",
        "date": "20/06/2022",
        "hour": "12",
        "minutes": "30",
        "testtype": "PCR"
    }, follow_redirects=True)
    myclient = pymongo.MongoClient("mongodb+srv://19179422:soft7011@cluster0.whl83.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    mydb = myclient["tests"]
    mycol = mydb["tests"]
    myquery = {"user": crownpassid}
    x = mycol.find(myquery)
    lengthAfter = len(list(x))
    myquery = {"testCentre": "Sample Testing Centre"}
    mycol.delete_one(myquery)
    assert (response.status_code == 200 and lengthAfter > lengthBefore)


def test_bookVaccination(clientBooker):
    '''
    Test ran to verify that the COVID-19 vaccination can be successfully booked.
    The length of the tests table of the database is measured before and
    after the POST request.
    :return: Response 200 for the POST request, and an assertion that
    verifies that the array of vaccinations for that user is larger than before.
    '''
    crownpassid = 1
    arrayVacs = list(Vaccine.get_by_id(crownpassid))
    lengthBefore = len(arrayVacs)
    response = clientBooker.post("/book", data={
        "vacCentre": "Sample Vaccination Centre",
        "date": "20/06/2022",
        "vacType": "Astrazeneca"
    }, follow_redirects=True)
    myclient = pymongo.MongoClient("mongodb+srv://19179422:soft7011@cluster0.whl83.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    mydb = myclient["vaccination"]
    mycol = mydb["vaccination"]
    myquery = {"user": crownpassid}
    x = mycol.find(myquery)
    lengthAfter = len(list(x))
    myquery = {"vacCentre": "Sample Vaccination Centre"}
    mycol.delete_one(myquery)
    assert (response.status_code == 200 and lengthAfter > lengthBefore)