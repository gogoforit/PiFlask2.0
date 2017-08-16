from mongoengine import *


class Remarks(Document):
    class_id = StringField(required=True)
    remarks = StringField(required=True)
    class_num = StringField(required=True)
    date = StringField(required=True)
    meta = {'db_alias': 'local_db'}