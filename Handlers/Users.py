import bcrypt
from flask import jsonify


class UserHandler:

    def get_user(self, request):
        return jsonify(user={'username': request.form['username']})

    def get_contacts(self, request):
        contacts = []
        contacts.append({'cid'})

    def insert_user(self, request):
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return jsonify(username=username, msg='Success'), 201

    def insert_contact(self, request):
        pass
