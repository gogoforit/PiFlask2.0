from mongoengine import *


class Student(Document):
    name = StringField(required=True)
    student_id = StringField(required=True)
    class_id = StringField(required=True)
    address_mac = StringField(required=True)
    meta = {'db_alias': 'local_db'}