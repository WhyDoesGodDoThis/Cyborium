#imports
from datetime import datetime as dt
#dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
from hashlib import sha256 as s5
from random import random as r
import os

#the file and chain finders
here = os.path.dirname(os.path.abspath(__file__))
block_file = os.path.dirname(os.path.abspath(__file__)) +"/blocks/block_file.txt"
#limit number of decimal digits to 2
def limit(x):
    x = float(x)
    if len(str(x).split('.')[1]) > 2:
        raise ValueError("too many decimal digits in amount of cyborium")
    return round(x, 2)
class block:
    #initialize block
    def __init__(self):
        global block_file
        #open block file
        blockfile = open(block_file)
        #get lines
        lines = blockfile.readlines()
        #set prev_hash
        self.prev_hash = s5(os.urandom(32)).hexdigest()
        #loop through lines backwards
        for line in lines[::-1][1:]:
            #if line starts with [Block Hash]
            if line.startswith('[Block Hash] '):
                #set prev_hash
                self.prev_hash = line[12:-1]
                #break loop
                break
        #set time made
        self.time_made = str(dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        #set data
        self.data = ""
        self.tip = 2
    #add item to block
    def add_item(self, item):
        if item.startswith('[Miner Tip] '):
            self.tip += limit(item.split(' -> ')[1])
        self.data += str(item) + ' ~Time~ ' + str(dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]) + '\n'
    #aprove hash
    def aprove_hash(self):
        global block_file
        user = input("Block Miner: ")
        #hash object
        hasher = s5()
        #increment
        increment = 6
        #loop until hash is aproved
        while True:
            #get time
            time = str(dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            #hash data
            hasher.update((
            str(self.data)+
            str(self.prev_hash)+
            str(self.time_made)+
            time+
            str(increment)
            ).encode()
            )
            #if hash starts with 000
            if hasher.hexdigest().startswith('000000'):
                #write block to file
                with open(block_file, 'a') as block_file_:
                    block_file_.write('[Start Block]\n')
                    block_file_.write('[Previous Hash] ' + self.prev_hash + '\n')
                    block_file_.write('[Time Made] ' + self.time_made + '\n')
                    block_file_.write(self.data)
                    block_file_.write('[Time Ended] ' + time + '\n')
                    block_file_.write('[block value] ' + str(increment) + '\n')
                    block_file_.write('[Block Hash] ' + hasher.hexdigest() + '\n')
                    block_file_.write('[Block Miner] ' + user + (' | Rewarded %d Cyborium' % self.tip) +'\n')
                    block_file_.write('[End Block]\n')
                    inc = 0
                    while True:
                        if s5((str(open(block_file).read()) + str(inc)).encode()).hexdigest().startswith('0000'):
                            block_file_.write('[Chain Hash] ' + s5((str(open(block_file).read()) + str(inc)).encode()).hexdigest() + '\n')
                            block_file_.write('[Chain Hash Time] ' + dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + '\n')
                            block_file_.write('[Chain Value] ' + str(inc) + '\n\n')
                            break
                        inc+= 1
                #print
                print("[Block Mined Successfully]")
                #return
                return 0
            #increment
            increment+=6

def transaction(amount, user, user_key, reciever, latest_block):
    if user == "SYSTEM":
        print('This username is restricted in standard transactions for security reasons.')
        return 0
    if reciever == "SYSTEM":
        print('This reciever can not recieve transactions.')
        return 0
    #get user number
    if user+'\n' in open(os.path.join(here, 'users.txt')).readlines():
        user_num = open(os.path.join(here, 'users.txt')).readlines().index(user+'\n')
    else:
        print('Transaction Failed: Invalid username or key.')
        return 0
    #if key is correct
    if s5(str(user_key).encode()).hexdigest() == open(os.path.join(here, 'hashes.txt')).readlines()[user_num][:-1]:
        #if user has enough money
        if get_balence(user) < amount:
            #tell user
            print("Transaction Failed: Not enough money")
            #return
            return 0
        #add transaction to block
        latest_block.add_item(
            "[Transaction] "+
            str(user)+' | '+
            str(s5(user_key.encode()).hexdigest())+' -> '+
            str(amount)+' -> '+
            str(reciever)
        )
        print("[Transaction Registered Successfully]")
    else:
        print("Transaction Failed: Invalid username or key.")
        return 0

def tip(latest_block):
    user = input('Username: ')
    user_key = s5(input('Key: ').encode()).hexdigest()
    if user == "SYSTEM":
        print('This username is restricted in standard tips for security reasons.')
        return 0
    #get user number
    if user+'\n' in open(os.path.join(here, 'users.txt')).readlines():
        user_num = open(os.path.join(here, 'users.txt')).readlines().index(user+'\n')
    else:
        print("Tip Failed: Invalid username or key.")
        return 0
    #if key is correct
    if user_key == open(os.path.join(here, 'hashes.txt')).readlines()[user_num][:-1]:
        amount = input('Amount: ')
        if get_balence(user) < limit(amount):
            print('Tip Failed: Invalid not enough Cyborium')
            return 0
        latest_block.add_item(
            '[Miner Tip] '+
            user+
            ' | '+
            user_key+
            ' -> '+amount
        )
        print('[Tip Registered Successfully]')
    else:
        print("Tip Failed: Invalid username or key.")
        return 0

def get_balence(user):
    global block_file
    #get user number
    user_num = open(os.path.join(here, 'users.txt')).readlines().index(user+'\n')
    #get user balence
    balence = 0
    #loop through blocks
    for block in open(block_file).readlines():
        #if block starts with [Start Block]
        if block.startswith('[Start Block]'):
            #set in_block to true
            in_block = True
        #if block starts with [End Block]
        if block.startswith('[End Block]'):
            #set in_block to false
            in_block = False
        #if in block
        if in_block:
            #if block starts with [Transaction]
            if block.startswith('[Transaction] '):
                #if user is in transaction
                if user in block:
                    #if user is reciever
                    if user == block.split(' -> ')[2].split(' ~Time~ ')[0]:
                        #add amount to balence
                        balence += limit(block.split(' -> ')[1])
                    #if user is sender
                    if user == block.split(' -> ')[0].split(' | ')[0].split('[Transaction] ')[1] and open(os.path.join(here, 'hashes.txt')).readlines()[user_num][:-1] == block.split(' -> ')[0].split(' | ')[1]:
                        #subtract amount from balence
                        balence -= limit(block.split(' -> ')[1])
            if block.startswith('[Block Miner] '):
                if user in block:
                    balence += limit(block.split(' Cyborium')[0].split('Rewarded ')[1])
            if block.startswith('[Miner Tip] '):
                if user in block:
                    balence -= limit(block.split(' -> ')[1].split(' ~Time~ ')[0])
    #return balence
    return balence

def make_user():
    #loop until username is not taken
    while True:
        #get username
        username = input("Choose a username:")
        #if username is taken
        if username+'\n' in open(os.path.join(here, 'users.txt')).readlines():
            #tell user
            print("Username already chosen pick again.")
            #restart loop
            continue
        #break loop
        break
    #get key
    key = input("Make a secure random key and save it some where as well as your username:")
    #write username to file
    open(os.path.join(here, 'users.txt'), 'a').write(username+'\n')
    #write hash of key to file
    open(os.path.join(here, 'hashes.txt'), 'a').write(s5(key.encode()).hexdigest()+'\n')

#initialize first block
latest = block()

#loop
while True:
    #get user input
    userinput = int(input('\n\n\nchoose:\n1. make user\n2. run transaction\n3. tip block miner\n4. add mock item to block\n5. minse block\n6. get acount value\n7. exit\n>>>'))
    #if user wants to make user
    if userinput == 1:
        #make user
        make_user()
        #restart loop
        continue
    #if user wants to run transaction
    if userinput == 2:
        #get username
        username = input('Username: ')
        #get key
        keypass = input('Key: ')
        #get amount
        amount = limit(input("Amount: "))
        #get target
        target = input('Reciever: ')
        #run transaction
        transaction(amount, username, keypass, target, latest)
        #restart loop
        continue
    #to tip the Miner
    if userinput == 3:
        tip(latest)
        continue
    #if user wants to add mock data
    if userinput == 4:
        #add mock data
        latest.add_item("[Mock Data] " + s5(str(r()).encode()).hexdigest())
        #restart loop
        continue
    #if user wants to mine block
    if userinput == 5:
        #mine block
        latest.aprove_hash()
        #initialize new block
        latest = block()
        #restart loop
        continue
    #check balence
    if userinput == 6:
        print(get_balence(input('Username: ')))
        continue
    #if user wants to exit
    if userinput == 7:
        break