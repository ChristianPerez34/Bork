import bcrypt
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, \
    jwt_required
from flask_restful import Resource, reqparse

from Handlers.Chat import ChatHandler
from Handlers.Users import UserHandler


class Index(Resource):

    def get(self):
        return jsonify(msg='Hello World')


class UserRegistration(Resource):

    def post(self):
        """
        Registers new user
        :return: JSON
        """
        parser = reqparse.RequestParser()
        parser.add_argument('username', help='Username field cannot be blank', required=True)
        parser.add_argument('email', help='Email field cannot be blank', required=True)
        parser.add_argument('password', help='Password field cannot be blank', required=True)

        # Verifies needed parameters to register users are present
        data = parser.parse_args()

        # Dummy data for phase I of project
        username = 'new_user'
        email = 'new_user@bork.com'
        password = 'password'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = UserHandler().insert_user(username=username, email=email, password=hashed_password)
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        user = {
            'uid': user_id,
            'username': username,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return jsonify(user=user)


class UserLogin(Resource):

    def post(self):
        """
        Logs in existing user
        :return: JSON
        """
        parser = reqparse.RequestParser()
        parser.add_argument('username', help='Username field cannot be blank', required=True)
        parser.add_argument('password', help='Password field cannot be blank', required=True)

        # Verifies needed parameters to register users are present
        data = parser.parse_args()

        # Dummy data for Phase I

        # TODO: add verify password method.
        username = 'ninja'
        password = 'password'
        user = UserHandler().get_user(username)
        is_authenticated = bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
        if is_authenticated:
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            user = {
                'uid': user['uid'],
                'username': username,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            user = {
                'msg': 'Invalid credentials'
            }
        return jsonify(user=user, is_authenticated=is_authenticated)


class Users(Resource):

    @jwt_required
    def get(self):
        users = UserHandler().get_users()
        return jsonify(users=users)


class User(Resource):

    @jwt_required
    def get(self):
        user = UserHandler().get_user(username='ninja')
        return jsonify(user=user)

    @jwt_required
    def post(self):
        pass

    @jwt_required
    def put(self):
        pass


class Chats(Resource):

    @jwt_required
    def get(self):
        return ChatHandler().get_chats()


class Contacts(Resource):

    def get(self):
        """
        Retrieves all contacts from database
        :return: JSON
        """
        return jsonify(contacts=0)


class Contact(Resource):

    def get(self, user_id):
        """
        Retrieves contact from database for specified user id
        :return: JSON
        """
        return jsonify(contact=0)

    def post(self, user_id):
        """
        Adds a new contact for specified user id
        :return: JSON
        """
        return jsonify(contact=0)


class Chat(Resource):

    def get(self, chat_id):
        return ChatHandler().get_chat(chat_id)

    def post(self):
        chat = {'id': 2, 'chat_name': 'Videout'}
        return jsonify(chat=chat, msg='Success')


class ChatMessages(Resource):

    def get(self, chat_id):
        """
        Gets all messages from given chat id.
        :param chat_id: id of the chat messages are to be extracted from
        :return: JSON representation of messages table
        """
        messages = ChatHandler().get_chat_messages(chat_id)
        return jsonify(messages=messages)


class TokenRefresh(Resource):

    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return jsonify(access_token=access_token)