import datetime

import bcrypt
from dateutil.relativedelta import relativedelta
from flask import jsonify, json
from flask_jwt_extended import get_jwt_identity, create_access_token, create_refresh_token
from psycopg2._psycopg import IntegrityError

from dao.user_dao import UserDAO


class UserHandler:

    def __init__(self):
        self.password = 'password'
        self.first_name = 'first_name'
        self.last_name = 'last_name'
        self.email = 'email'
        self.phone = '7875555555'
        self.dao = UserDAO()

    def get_users(self):
        """
        Gets all users
        :return: RealDictCursor
        """
        return self.dao.get_all_users()

    def get_user_by_username(self, username):
        """
        Gets user by username
        :param username: str
        :return: RealDictCursor
        """
        return self.dao.get_user_by_username(username)

    def get_user_by_id(self, uid):
        """
        Gets user by id
        :param uid: int
        :return: RealDictCursor
        """
        return self.dao.get_user(uid)

    def get_contacts(self, user_id):
        """
        Gets user contacts
        :param user_id: int
        :return: RealDictCursor
        """
        return self.dao.get_contacts(user_id)

    def insert_contact(self, data):
        """
        Adds new contact for user
        :param data: dict
        :return: RealDictCursor
        """
        owner_username = get_jwt_identity()
        owner_user = self.dao.get_user_by_username(owner_username)['uid']
        try:
            first_name = data['first_name']
            last_name = data['last_name']
            phone_number = data['phone_number']
            email = data['email']
        except KeyError:
            return jsonify(msg='Missing parameters')
        try:
            if phone_number:
                contact_to_add = self.dao.get_user_by_phone_number(data['phone_number'])['uid']
            elif email:
                contact_to_add = self.dao.get_user_by_email(data['email'])['uid']
            else:
                return jsonify(msg='Missing parameters')
        except IndexError:
            return jsonify(msg='User does not exist')
        self.dao.insert_contact(owner_user, contact_to_add, first_name, last_name)
        return jsonify(msg="Added contact successfully")

    def update_contact(self, contact_id):
        contact = {
            'contact_id': 3,
            'uid': 4
        }
        return contact

    def insert_user(self, data):
        """
        Handles user data to be sent to the dao for further actions
        :param data: dict
        :return: JSON
        """
        invalid_data = {k: v for k, v in data.items() if not v}
        if invalid_data:
            response_data = json.dumps({
                'message': 'These fields must be filled',
                'fields': [k for k in invalid_data.keys()]})
            response_status = 400
        else:
            username = data['username']
            email = data['email']
            password = bcrypt.hashpw(data['password'].encode('utf-8'),
                                     bcrypt.gensalt()).decode('utf-8')
            first_name = data['first_name']
            last_name = data['last_name']
            phone_number = data['phone_number']

            # Generates JWT access and refresh tokens for user.
            access_token = create_access_token(identity=username,
                                               expires_delta=datetime.timedelta(days=365))
            refresh_token = create_refresh_token(identity=username)

            try:
                uid = self.dao.insert_user(username, password, first_name,
                                           last_name, email, phone_number)
                user = {
                    'user': {
                        'uid': uid,
                        'username': username,
                        'access_token': access_token,
                        'refresh_token': refresh_token
                    }
                }
                response_data = json.dumps(user)
                response_status = 200
            except IntegrityError:
                response_data = json.dumps({
                    'message': f'User with username: "{username}" exists',
                    'fields': ['username']})
                response_status = 400
        return response_data, response_status

    def verify_password(self, data):
        """
        Verifies user credentials
        :param data: dict
        :return: tuple
        """
        if data['username'] and data['password']:
            username = data['username']
            password = data['password']
            db_password = self.dao.get_user_password(username)
            user = self.dao.get_user_by_username(username)
            is_authenticated = bcrypt.checkpw(password.encode('utf-8'),
                                              db_password.encode('utf-8')) if db_password else False
            if is_authenticated:
                access_token = create_access_token(identity=user['username'],
                                                   expires_delta=datetime.timedelta(days=365))
                refresh_token = create_refresh_token(identity=user['username'])
                user = {
                    'uid': user['uid'],
                    'username': user['username'],
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
                response_data = json.dumps(
                    {
                        'user': user,
                        'is_authenticated': is_authenticated
                    }
                )
                response_status = 200
            elif user is None:
                response_data = json.dumps({
                    'message': f'Username: "{username}" does not exist',
                    'fields': 'username'
                })
                response_status = 400
            else:
                response_data = json.dumps({
                    'message': 'Invalid credentials',
                    'fields': ['username', 'password']
                })
                response_status = 400
        else:
            response_data = json.dumps(
                {
                    'message': 'Username and password fields cannot be blank',
                    'fields': ['username', 'password']
                })
            response_status = 400
        return response_data, response_status

    def update_user_username(self, username, new_username):
        """
        Updates username
        :param username: str
        :param new_username: str
        :return: RealDictCursor
        """
        user = self.get_user_by_username(username)
        user['username'] = new_username
        return user

    def remove_contact(self, data):
        """
        Removes contact from users contacts list
        :param data: dict
        :return: JSON
        """
        contact_id = data['contact_id']
        username = get_jwt_identity()
        uid = self.dao.get_user_by_username(username)['uid']
        self.dao.delete_contact(uid, contact_id)
        new_contacts = self.dao.get_contacts(uid)
        return jsonify(contacts=new_contacts)

    def get_daily_active_users(self):
        """
        Gets daily active users
        :return: JSON
        """
        today = datetime.datetime.today()
        users = []
        for i in range(7):
            day_to_get = today - relativedelta(days=i)
            num = self.dao.get_daily_active_users(day_to_get)
            users.append({'day': '%s' % day_to_get, 'users': num})
        return jsonify(users)

    def get_num_messages_user(self, uid):
        """
        Gets daily number of messages posted by user
        :param uid: int
        :return: JSON
        """
        today = datetime.datetime.today()
        num_messages = []
        for i in range(7):
            day_to_get = today - relativedelta(days=i)
            num = self.dao.get_daily_messages_user(day_to_get, uid)
            num_messages.append({
                'username': num['username'],
                'day': day_to_get,
                'total': num['num']
            })
        return jsonify(num_messages)
