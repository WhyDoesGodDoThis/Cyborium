from datetime import datetime as dt
#dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
from hashlib import sha256 as s5


class block:
    def __init__(self, data, previous_hash):
        self.prev_hash = previous_hash
        self.time_made = str(dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        self.data = ""
    def add_item(self, item):
        self.data += str(item) + ' ' + str(dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]) + '\n'
    def aprove_hash(self):
        hasher = s5()
        increment = 6
        while True:
            time = str(dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            hasher.update((
            str(self.data)+
            str(self.prev_hash)+
            str(self.time_made)+
            time+
            str(increment)
            ).encode()
            )
            if hasher.hexdigest().startswith('000'):
                return hasher.hexdigest()
            increment+=6

def transaction(self, amount, user, user_key, reciever, latest_block):
    user_num = open('users/users.txt').readlines().index(user)
    if s5(str(user_key).encode()).hexdigest() == open('users/hashes.txt').readlines()[user_num]:
        latest_block.add_item(
            str(user)+' | '+
            str(user_key)+' -> '+
            str(amount)+' -> '+
            str(reciever)
        )