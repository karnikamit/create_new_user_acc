# -*- coding: utf-8 -*-
__author__ = "karnikamit"
from passlib.context import CryptContext
from schema import Schema, SchemaError, And
import password_generator
from itsdangerous import JSONWebSignatureSerializer
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "des_crypt"], default="pbkdf2_sha256",
                           all__vary_rounds=0.1, pbkdf2_sha256__default_rounds=8000)
from create_new_user_acc import User
from mongoengine import connect


def password_validate(username, password):
    success, error = False, False
    user_details = User.objects(username=username).first()
    if user_details:
        try:
            if pwd_context.verify(password, user_details.password) and user_details.is_active:
                success = True
            else:
                error = "Invalid password or account not activated by admin."
        except Exception, message:
            print 'Exceptioin: %s' % message.message
            error = "Invalid password or account not activated by admin."
    else:
        error = "Username not found."

    return {'success': success, 'error': error}


def valid_email(input_email):
    from validate_email import validate_email

    is_valid = validate_email(input_email)
    email_exists = User.objects(email=input_email).first()
    if is_valid and not email_exists:
       return True
    else:
       return False


def valid_username(input_username):
    user_exists = User.objects(username=input_username).first()
    if user_exists:
        return False
    else:
        return True


def valid_roles(role_list):
    good_role = True
    roles = ['regular']
    if roles:
       for role in role_list:
           if role not in roles:
               good_role = False
    else:
       good_role = False
    return good_role


def create_account(data, db_name):
    """

    :param data: User Details
    :param db_name: MongoDb name to store the data
    :return: response
    """
    connect(db_name)
    success = error = False
    if 'role' not in data.keys():
       data['role'] = ['regular']
    try:

        if 'password_verify' in data.keys():
            del data['password_verify']
        if 'is_active' not in data.keys():
            data['is_active'] = True
        data = dict(data)
        Schema({
            'fullname': And(basestring, lambda n: len(n) > 3, error="Full name not valid"),
            'username': And(basestring, lambda n: len(n) > 4, valid_username,
                            error="Username not valid or already in use"),
            'email': And(basestring, valid_email, error="Email not valid or already in use"),
            'password': And(basestring, error="Password not valid"),
            'is_active': And(bool, error="Active state not valid"),
            'role': And(valid_roles, error="Role not valid")
        }).validate(data)
    except SchemaError as e:
        error = e.message
        return {'success': success, 'error': error}
    try:
        api_key = password_generator.generate(length=16)
        api_secret = password_generator.generate(length=16)
        serializer = JSONWebSignatureSerializer(api_key, salt=api_secret)
        api_token = serializer.dumps({'user_id': data['username']})
        api_doc = {'key': api_key, 'secret': api_secret, 'token': api_token}
        user = User(fullname=data['fullname'], username=data['username'], email=data['email'],
                    password=pwd_context.encrypt(data['password']), is_active=data['is_active'],
                    roles=data['role'], apicred=api_doc)
        user.save()
        success = True
    except:
        success = False
        error = "Error occurred while registering. Please contact EdGE Networks"
    return {'success': success, 'error': error}

