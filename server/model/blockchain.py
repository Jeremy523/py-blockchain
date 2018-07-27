'''
The Blockchain data structures and utilities needed to facilitate the concurrent blockchain
application server-side.

Jeremy De La Cruz
'''

import hashlib
import calendar
import json
import time


class Blockchain:
    def __init__(self):
        self.chain = []

    def replace_if_needed(self, other_blockchain):
        if other_blockchain.len() > self.len():
            self.chain = other_blockchain.chain

    def first(self):
        return self.chain[0] if self.len() > 0 else None

    def last(self):
        return self.chain[self.len() - 1] if self.len() > 0 else None

    def add(self, block):
        self.chain.append(block)
        return self

    def len(self):
        return len(self.chain)

    def __str__(self):
        chain_string = ''
        for block in self.chain:
            chain_string += 'block' + str(block.index) + ':' + str(block) + '\n'
        return chain_string

    def to_json(self):
        blocks = []
        for block in self.chain:
            blocks.append( block.to_obj() )
        return json.dumps(blocks)


class Block:
    def __init__(self, index, timestamp, sender, receiver, transaction_amt, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver
        self.transaction_amt = transaction_amt
        self.prev_hash = prev_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        return hash (
            str(self.index)
            + str(self.timestamp)
            + str(self.sender)
            + str(self.receiver)
            + str(self.transaction_amt)
            + str(self.prev_hash)
        )

    def __str__(self):
        return json.dumps( self.to_obj() )

    def to_obj(self):
        return {
            'index' : self.index,
            'timestamp' : self.timestamp,
            'sender' : self.sender,
            'receiver' : self.receiver,
            'transaction_amt' : self.transaction_amt,
            'prev_hash' : self.prev_hash,
            'hash' : self.hash
        }

# get current time
def get_time():
    return str( calendar.timegm( time.gmtime() ) )

# hash a given string using SHA256
def hash(str):
    return hashlib.sha256(str.encode('utf-8')).hexdigest()

# initialize the blockchain with genesis block
def init_blockchain():
    blockchain = Blockchain()
    genesis_block = Block(0, get_time(), '', '', 0, '')
    new_blockchain = blockchain.add(genesis_block)
    blockchain.replace_if_needed(new_blockchain)
    return blockchain

# generate a new block using the previous block's hash on the blockchain
def generate_block(old_block, sender, receiver, transaction_amt):
    return Block(old_block.index + 1, get_time(), sender, receiver, transaction_amt, old_block.hash)

# validate if the blocks' hashes line up
def is_block_valid(new_block, old_block):
    return (
        old_block.index + 1 == new_block.index
        and old_block.hash == new_block.prev_hash
        and new_block.calc_hash() == new_block.hash
    )

