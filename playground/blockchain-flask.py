from flask import Flask, abort, jsonify, make_response, request
import hashlib
import calendar
import time
import threading


class Blockchain:
    def __init__(self):
        self.chain = []

    def replaceIfNeeded(self, otherBlockchain):
        if otherBlockchain.len() > self.len():
            self.chain = otherBlockchain.chain

    def first(self):
        return self.chain[0] if self.len() > 0 else None

    def last(self):
        return self.chain[self.len() - 1] if self.len() > 0 else None

    def add(self, block):
        self.chain.append(block)
        return self

    def len(self):
        return len(self.chain)


class Block(threading.Thread):
    def __init__(self, index, timestamp, sender, receiver, transactionAmt, prevHash):
        self.index = index
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver
        self.transactionAmt = transactionAmt
        self.prevHash = prevHash
        self.hash = self.calcHash()

    def calcHash(self):
        return hash(str(self.index) + str(self.timestamp) + str(self.sender) + str(self.receiver) + str(self.transactionAmt) + str(self.prevHash))

    def toString(self):
        return {
            'index' : self.index,
            'timestamp' : self.timestamp,
            'sender' : self.sender,
            'receiver' : self.receiver,
            'transactionAmt' : self.transactionAmt,
            'prevHash' : self.prevHash,
            'hash' : self.hash
            }


def getTime():
    return str(calendar.timegm(time.gmtime()))

def hash(str):
    return hashlib.sha256(str.encode('utf-8')).hexdigest()

def generateBlock(oldBlock, sender, receiver, transactionAmt):
    return Block(oldBlock.index + 1, getTime(), sender, receiver, transactionAmt, oldBlock.hash)

def isBlockValid(newBlock, oldBlock):
    return oldBlock.index+1 == newBlock.index and oldBlock.hash == newBlock.prevHash and newBlock.calcHash() == newBlock.hash


app = Flask(__name__)
blockchain = Blockchain()

@app.route('/', methods=['GET'])
def getBlockchain():
    jsonBlocks = []
    for block in blockchain.chain:
        jsonBlocks.append(block.toString())
    if len(jsonBlocks) > 0:
        return make_response(jsonify(jsonBlocks), 200)
    abort(400)

@app.route('/', methods=['POST'])
def writeBlock():
    if not request.json or not 'sender' in request.json or not 'receiver' in request.json or not 'transactionAmt' in request.json:
        abort(400)
    if blockchain.len() == 0:
        newBlock = Block(0, getTime(), request.json['sender'], request.json['receiver'], request.json['transactionAmt'], '')
    else:
        newBlock = generateBlock(blockchain.last(), request.json['sender'], request.json['receiver'], request.json['transactionAmt'])
        if not isBlockValid(newBlock, blockchain.last()):
            abort(400)
    newBlockchain = blockchain.add(newBlock)
    blockchain.replaceIfNeeded(newBlockchain)

    jsonBlocks = []

    for block in blockchain.chain:
        jsonBlocks.append(block.toString())

    return make_response(jsonify(jsonBlocks), 200)


if __name__ == '__main__':
    app.run()
