# -*- coding: utf-8 -*-
__author__ = "karnikamit"
from mongoengine import *
import datetime


class User(DynamicDocument):
    fullname = StringField(required=True)
    email = StringField(required=True, unique=True, primary_key=True)
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    is_active = BooleanField(required=True, default=True)
    date_modified = DateTimeField(default=datetime.datetime.now)
    roles = ListField(field=StringField(), default=['regular'])
    apicred = DictField()
    inserted_at = StringField(default=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username
