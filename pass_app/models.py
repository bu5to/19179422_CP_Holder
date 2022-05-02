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


class Crownpass:
    def __init__(self, crownpassid, infStatus, vacStatus):
        self.crownpassid = crownpassid
        self.infStatus = infStatus
        self.vacStatus = vacStatus

    def get_by_id(crownpassid):
        myclient = pymongo.MongoClient(os.environ.get('MONGO_CLIENT'))
        mydb = myclient["crownpass"]
        mycol = mydb["crownpass"]
        x = mycol.find_one({"crownpassid": int(crownpassid)})
        cpass = Crownpass(x['crownpassid'], x['infStatus'], x['vacStatus'])
        return cpass

    def parseToDict(self):
        strDict = {
            "crownpassid": self.crownpassid,
            "infStatus": self.infStatus,
            "vacStatus": self.vacStatus
        }
        return strDict
