import redis
import json

class Database:
    def __init__(self):
        self.r = redis.StrictRedis()

    def get_new_id(self):
        return self.r.incr('<next_object_id>')

    def account_id(self, email, id=None):
        """
            return id for corresponding email
            set id when it is not None
        """
        if id is not None:
            return self.r.set('account:email:{}'.format(email.lower()), id)
        else:
            return self.r.get('account:email:{}'.format(email.lower()))

    def account_email(self, id, email=None):
        """
            return email for corresponding id
            set email when it is not None
        """
        if email is not None:
            return self.r.set('account:{}:email'.format(id), email.lower())
        else:
            return self.r.get('account:{}:email'.format(id))

    def account_password(self, id, password=None):
        """
            return password for corresponding id
            set password when it is not None
        """
        if password is not None:
            return self.r.set('account:{}:password'.format(id), password)
        else:
            return self.r.get('account:{}:password'.format(id))

    def user_nickname(self, id, nickname=None):
        """
            return nickname for corresponding id
            set nickname when it is not None
        """
        if nickname is not None:
            return self.r.set('user:{}:nickname'.format(id), nickname)
        else:
            return self.r.get('user:{}:nickname'.format(id))

    def user_avatar(self, id, avatar=None):
        """
            return avatar for corresponding id
            set avatar when it is not None
        """
        # TODO
        pass

    # def user_friendlist(self, id, add_id=None):
    #     """
    #         return friendlist for corresponding id, usually use user_friendgroup
    #         add a new friend if add_id is not None
    #     """
    #     pass

    def user_friendgroup(self, id, new_group=None):
        """
            return grouplist and friend id in them for corresponding id
            [
                {
                    group_name: str
                    group_id: str
                    [friendlist]
                }
            ]
            add a new empty group if new_group is not None
        """
        if new_group is not None:
            return self.r.lpush('user:{}:friendgroup'.format(id), json.dumps({'group_name': new_group, 'group_id': self.get_new_id(), 'friendlist': []}))
        else:
            return self.r.lrange('user:{}:friendgroup'.format(id), 0, 100)

    def user_del_friend_group(self, group_id):
        pass

    def user_add_to_friendgroup(self, id, new_group, pre_group, friend_id):
        """
            move a friend to a another group
        """
        pass

    def user_add_friend(self, id, friend_id, group):
        pass

    def user_del_friend(self, id, group, friend_id):
        """
            delete a friend from a friend group
        """
        pass

    def user_online(self, id, set=False):
        if set:
            return self.r.set('user:{}:isonline'.format(id), True)
        else:
            return self.r.get('user:{}:isonline')

    def user_offline(self, id):
        return self.r.set('user:{}:isonline'.format(id), False)

    def message_sent(self, sender, receiver, message):
        """
            when message has been sent, put this message into sender's db
        """
        return self.r.lpush('message:{}:send:{}'.format(sender, receiver), message)

    def message_received(self, sender, receiver, message):
        """
            when message has been sent, put this message into receiver's db
            if it cannot be sent right now, put it into a waiting queue
        """
        return self.r.lpush('message:{}:received:{}'.format(receiver, sender), message)


    def message_processing_wating(self, sender, receiver, message):
        """
            check if the receiver has any message that is waiting for receiving
        """
        return self.r.lpush('message:{}:waiting'.format(receiver), {'message': message, 'sender': sender})

    def get_wating_messsage(self, receiver):
        return self.r.lpop('message:{}:wating'.format(receiver))


db = Database()
