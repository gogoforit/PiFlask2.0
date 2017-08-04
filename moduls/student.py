from mongoengine import *


class Student(Document):
    _id = StringField()
    name = StringField(required=True)
    student_id = StringField(required=True)
    class_id = StringField(required=True)
    address_mac = StringField(required=True)