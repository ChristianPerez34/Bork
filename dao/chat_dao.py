from dao.dao import DAO


class ChatDAO(DAO):

    def get_chat_messages(self, cid):
        """
        Gets all messages belonging to specified chat with given id
        :param cid: int
        :return: RealDictCursor
        """
        cursor = self.get_cursor()
        query = "WITH replies_query AS (SELECT reply, message AS replies_list " \
                "FROM replies INNER JOIN messages ON replies.replied_to =  messages.mid " \
                "GROUP BY reply, message), like_count AS (SELECT mid, COUNT(*) AS likes " \
                "FROM vote WHERE upvote = TRUE GROUP BY mid), " \
                "dislike_count AS (SELECT mid, COUNT(*) AS dislikes " \
                "FROM vote WHERE upvote = FALSE GROUP BY mid) " \
                "SELECT messages.mid, users.uid, cid, message, image, " \
                "COALESCE(likes, 0) AS likes, COALESCE(dislikes, 0) AS dislikes, " \
                "username, COALESCE(replies_list, NULL) AS replies, messages.created_on " \
                "FROM messages LEFT OUTER JOIN like_count ON messages.mid = like_count.mid " \
                "LEFT OUTER JOIN dislike_count ON messages.mid = dislike_count.mid " \
                "LEFT OUTER JOIN photo ON messages.mid = photo.mid " \
                "INNER JOIN users ON messages.uid = users.uid " \
                "LEFT OUTER JOIN replies_query ON messages.mid = replies_query.reply " \
                "WHERE messages.cid = %s " \
                "ORDER BY messages.created_on DESC"
        cursor.execute(query, (cid,))
        messages = cursor.fetchall()
        return messages

    def get_all_chats(self):
        """
        Gets all chats from database
        :return: RealDictCursor
        """
        cursor = self.get_cursor()
        query = "select * from chat_group"
        cursor.execute(query)
        return cursor.fetchall()

    def get_chat(self, cid):
        """
        Gets chat with given id from database
        :param cid: int
        :return: RealDictCursor
        """
        cursor = self.get_cursor()
        query = 'SELECT chat_group.cid, chat_group.name, chat_group.uid, ' \
                'messages.message, messages.created_on, chat_group.uid ' \
                'FROM chat_group LEFT OUTER JOIN messages ON messages.cid = chat_group.cid ' \
                'WHERE chat_group.cid = %s LIMIT 1'
        cursor.execute(query, (cid,))
        return cursor.fetchall()

    def get_members_from_chat(self, cid):
        """
        Gets chat members from specified chat
        :param cid: int
        :return: RealDictCursor
        """
        cursor = self.get_cursor()
        query = 'WITH ChatMembers as (SELECT cid, uid FROM chat_members ' \
                'UNION SELECT cid, uid FROM chat_group)' \
                'SELECT uid, username ' \
                'FROM  ChatMembers NATURAL INNER JOIN users ' \
                'WHERE cid = %s'
        cursor.execute(query, (cid,))
        return cursor.fetchall()

    def get_owner_of_chat(self, cid):
        """
        Gets owner of chat from database
        :param cid: int
        :return: RealDictCursor
        """
        cursor = self.get_cursor()
        query = 'SELECT users.uid, users.username, users.first_name, users.last_name, ' \
                'users.email, users.phone_number ' \
                'FROM chat_group INNER JOIN users ON chat_group.uid = users.uid ' \
                'WHERE chat_group.cid = %s'
        cursor.execute(query, (cid,))
        return cursor.fetchall()

    def insert_chat_group(self, chat_name, owner_id, members=None):
        """
        Inserts a new chat group to the DB
        :param chat_name: str
        :param owner_id: int
        :param members: list containing uids of users to add
        :return: int
        """
        cursor = self.get_cursor()
        query = 'INSERT INTO chat_group (name, uid) VALUES (%s, %s) RETURNING cid, created_on'
        cursor.execute(query, (chat_name, owner_id))
        results = cursor.fetchall()
        cid = results[0]['cid']
        created_on = results[0]['created_on']
        self.commit()
        if members:
            for member in members:
                self.insert_member(cid, member)
        return cid, created_on

    def insert_member(self, cid, member_to_add):
        """
        Inserts a new chat_member on the DB
        :param cid: int
        :param member_to_add: int
        """
        cursor = self.get_cursor()
        query = "insert into chat_members (cid, uid) values (%s, %s)"
        cursor.execute(query, (cid, member_to_add,))
        self.commit()

    def get_user_chats(self, uid):
        """
        Gets all the chats that the user is a member in and chats the the user owns from the DB
        :param uid: int
        :return: RealDictCursor
        """
        cursor = self.get_cursor()
        query = 'WITH MyChats AS (SELECT cid, uid FROM chat_members WHERE uid = %s ' \
                'UNION ' \
                'SELECT cid, uid FROM chat_group WHERE uid = %s)' \
                'SELECT chat_group.cid, chat_group.uid, chat_group.name, chat_group.created_on ' \
                'FROM chat_group INNER JOIN MyChats ON chat_group.cid = MyChats.cid'
        cursor.execute(query, (uid, uid))
        return cursor.fetchall()

    def remove_member(self, cid, member_to_remove):
        """
        Removes chat member from specified chat
        :param cid: int
        :param member_to_remove: int
        """
        cursor = self.get_cursor()
        query = 'DELETE FROM chat_members WHERE cid = %s AND uid = %s'
        cursor.execute(query, (cid, member_to_remove))
        self.commit()

    def delete_chat(self, cid):
        """
        Deletes chat from database
        :param cid: int
        """
        cursor = self.get_cursor()
        query = 'DELETE FROM chat_group WHERE cid = %s'
        cursor.execute(query, (cid,))
        self.commit()
