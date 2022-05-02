import pymongo
import os


class User:
    def __init__(self, crownpassid, photo, qr, phone, email, home, name, gender, birthdate):
        self.crownpassid = crownpassid
        self.photo = photo
        self.qr = qr
        self.phone = phone
        self.email = email
        self.home = home
        self.name = name
        self.gender = gender
        self.birthdate = birthdate

    def get_by_id(crownpassid):
        myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
        mydb = myclient["users"]
        mycol = mydb["users"]
        x = mycol.find_one({"crownpassid": int(crownpassid)})
        user = User(x['crownpassid'], x['photo'], x['qr'], x['phone'], x['email'],
                    x['home'], x['name'], x['gender'], x['birthdate'])
        return user

    def parseToDict(self):
        strDict = {
            "crownpassid": self.crownpassid,
            "photo": self.photo,
            "qr": self.qr,
            "phone": self.phone,
            "email": self.email,
            "home": self.home,
            "name": self.name,
            "gender": self.gender,
            "birthdate": self.birthdate
        }
        return strDict


class Trace:
    def __init__(self, user, date, area, check):
        self.user = user
        self.date = date
        self.area = area
        self.check = check

    def get_by_id(crownpassid):
        myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
        mydb = myclient["tracing"]
        mycol = mydb["tracing"]
        x = mycol.find({"crownpassid": int(crownpassid)})
        return x

    def wipeTracing(crownpassid):
        myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
        mydb = myclient["tracing"]
        mycol = mydb["tracing"]
        query = mycol.find({"crownpassid": int(crownpassid)})
        mycol.delete_many(query)


class CovidTest:
    def __init__(self, user, date, testCentre, testType, result):
        self.user = user
        self.date = date
        self.testCentre = testCentre
        self.testType = testType
        self.result = result

    def get_by_id(crownpassid):
        myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
        mydb = myclient["tests"]
        mycol = mydb["tests"]
        x = mycol.find({"user": int(crownpassid)})
        listDict = list(x)
        arrayTests = []
        for element in listDict:
            arrayTests.append(
                CovidTest(element['user'], element['date'], element['testCentre'], element['type'], element['result']))
        return arrayTests

    def setColor(colour, crownpassid):
        myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
        filter = {'user': crownpassid}
        filter2 = {'crownpassid': crownpassid}
        if colour == "red":
            newvalues = {"$set": {'result': 'Positive'}}
            newvalues2 = {"$set": {'infStatus': 'Confirmed infection'}}
        if colour == "amber":
            newvalues = {"$set": {'result': 'Positive'}}
            newvalues2 = {"$set": {'infStatus': 'Suspected of infection'}}
        if colour == "green":
            newvalues = {"$set": {'result': 'Negative'}}
            newvalues2 = {"$set": {'infStatus': 'No infection'}}
        mydb = myclient["tests"]
        mycol = mydb["tests"]
        mycol.update_one(filter, newvalues)
        mydb = myclient["crownpass"]
        mycol = mydb["crownpass"]
        mycol.update_one(filter2, newvalues2)


class Vaccine:
    def __init__(self, user, date, vacCentre, vacType):
        self.user = user
        self.date = date
        self.vacCentre = vacCentre
        self.vacType = vacType

    def get_by_id(crownpassid):
        myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
        mydb = myclient["vaccination"]
        mycol = mydb["vaccination"]
        x = mycol.find({"user": int(crownpassid)})
        listDict = list(x)
        arrayVac = []
        for element in listDict:
            arrayVac.append(
                Vaccine(element['user'], element['date'], element['vacCentre'], element['vacType']))
        return arrayVac
