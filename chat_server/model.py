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

    def user_check_in_friendlist(self, id, friend_id):
        return self.r.sismember('user:{}:friendlist'.format(id), friend_id)

    def user_friendlist(self, id):
        friendlist = self.r.smembers('user:{}:friendlist'.format(id))
        return dict(zip(friendlist, map(lambda x: {'user_nickname': x[0], 'user_isonline': "Online" if x[1] == 'True' else "Offline"}, zip(map(self.user_nickname, friendlist), map(self.user_online, friendlist)))))
        # return {'friendlist': map(lambda x: {"user_id": x[0], "user_nickname": x[1], "user_isonline": "Online" if x[2] == 'True' else "Offline"}, zip(friendlist, map(self.user_nickname, friendlist), map(self.user_online, friendlist)))}


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
            group_id = self.get_new_id()
            self.r.zadd('user:{}:friendgroup'.format(id), group_id, group_id)
            return self.r.hmset('user:{}:friendgroup:{}'.format(id, group_id), {'group_name': new_group, 'group_id': group_id, 'friendlist': []})
        else:
            group_list = self.r.zrange('user:{}:friendgroup'.format(id), 0, 100)
            friend_groups = []
            for group_id in group_list:
                values = self.r.hmget('user:{}:friendgroup:{}'.format(id, group_id), 'group_name', 'friendlist')
                friendlist = json.loads(values[1])
                friend_online_status = map(self.user_online, friendlist)
                friend_groups.append({'group_name': values[0], 'group_id': group_id, 'friend_online_count': len(filter(lambda x: x == 'True', friend_online_status)), 'friend_count': len(friendlist), 'friendlist': friendlist})
                # friend_groups.append({'group_name': values[0], 'group_id': group_id, 'friend_online_count': len(filter(lambda x: x == 'True', friend_online_status)), 'friend_count': len(friendlist), 'friendlist': map(lambda x: {"user_id": x[0], "user_nickname": x[1], "user_isonline": "Online" if x[2] == 'True' else "Offline"}, zip(friendlist, map(self.user_nickname, friendlist), friend_online_status))})
            return friend_groups

    def user_del_friend_group(self, id, del_group_id, merge_group_id):
        self.r.zrem('user:{}:friendgroup'.format(id), del_group_id)
        friendlist = json.loads(self.r.hget('user:{}:friendgroup:{}'.format(id, del_group_id), 'friendlist'))
        for friend_id in friendlist:
            self.user_add_friend(id, friend_id, merge_group_id)
        self.r.delete('user:{}:friendgroup:{}'.format(id, del_group_id))

    def user_add_to_friendgroup(self, id, new_group_id, pre_group_id, friend_id):
        """
            move a friend to a another group
        """
        # print id, new_group_id, pre_group_id, friend_id
        self.user_del_friend(id, friend_id, pre_group_id)
        self.user_add_friend(id, friend_id, new_group_id)

    def user_add_friend(self, id, friend_id, group_id, real_add = False):
        friendlist = json.loads(self.r.hget('user:{}:friendgroup:{}'.format(id, group_id), 'friendlist'))
        friendlist.append(friend_id)
        self.r.hset('user:{}:friendgroup:{}'.format(id, group_id), 'friendlist', json.dumps(friendlist))
        if real_add:
            self.r.sadd('user:{}:friendlist'.format(id), friend_id)
            self.r.sadd('user:{}:notificationset'.format(friend_id), id)

    def user_del_friend(self, id, friend_id, group_id = None, real_del = False):
        """
            delete a friend from a friend group
        """
        if group_id is None:
            group_list = self.r.zrange('user:{}:friendgroup'.format(id), 0, 100)
            for group_id_iter in group_list:
                friendlist = json.loads(self.r.hget('user:{}:friendgroup:{}'.format(id, group_id_iter), 'friendlist'))
                if friend_id in friendlist:
                    group_id = group_id_iter
                    friendlist.remove(friend_id)
                    break
        else:
            friendlist = json.loads(self.r.hget('user:{}:friendgroup:{}'.format(id, group_id), 'friendlist'))
            friendlist.remove(friend_id)
        self.r.hset('user:{}:friendgroup:{}'.format(id, group_id), 'friendlist', json.dumps(friendlist))
        if real_del:
            self.r.srem('user:{}:friendlist'.format(id), friend_id)
            self.r.srem('user:{}:notificationset'.format(friend_id), id)

    def user_online(self, id, set=False):
        if set:
            return self.r.set('user:{}:isonline'.format(id), True)
        else:
            return self.r.get('user:{}:isonline'.format(id))

    def user_offline(self, id):
        return self.r.set('user:{}:isonline'.format(id), False)

    def user_notification_set(self, id):
        return self.r.smembers('user:{}:notificationset'.format(id))

    def message_sent(self, sender, receiver, message):
        """
            when message has been sent, put this message into sender's db
        """
        return self.r.rpush('message:{}:send:{}'.format(sender, receiver), message)

    def message_received(self, sender, receiver, message):
        """
            when message has been sent, put this message into receiver's db
            if it cannot be sent right now, put it into a waiting queue
        """
        return self.r.rpush('message:{}:received:{}'.format(receiver, sender), message)

    def message_processing_wating(self, sender, receiver, message):
        """
            check if the receiver has any message that is waiting for receiving
        """
        return self.r.rpush('message:{}:waiting'.format(receiver), json.dumps({'message': message, 'sender': sender}))

    def get_wating_message(self, receiver):
        return self.r.lpop('message:{}:waiting'.format(receiver))


db = Database()
