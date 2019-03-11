# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 17:58:03 2019

@author: Josh John
"""
#Requires Flask >> pip install flask
# requies postman Http Client htpps://getpostman.com

#import libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
from urllib.parse import urlparse
from uuid import uuid4
import requests

# Create a BlockChain

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0') #creating the Genesis block
        self.nodes = set()
    
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain)+1, 'timestamp': str(datetime.datetime.now()),
                 'proof': proof, 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 -previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
                #print("Found")
                print(hash_operation)
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 -previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
            
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver, 
                                  'amount': amount})
        previous_block = self.get_previous_block()
        
        return previous_block['index'] + 1
        
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')  #advance placeholder
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
#Mining the Blockchain
#Calling Flask
app = Flask(__name__)

#node address
node_address = str(uuid4()).replace('-','')

#Blockchain
blockchain =Blockchain()       

#Mining a block
@app.route('/mine_block', methods = ['GET'])

#Creating address for nodes
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    previous_hash = blockchain.hash(previous_block)
    proof = blockchain.proof_of_work(previous_proof)
    blockchain.add_transaction(sender = node_address, receiver = 'TripleJay', amount = 10)
    block = blockchain.create_block(proof,previous_hash)
    
    response = {'message': 'Congratulations, you just mined a block!',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'previous_hash':block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

#getting the full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain':blockchain.chain,
                'length':len(blockchain.chain) }
    
    return jsonify(response), 200

#check if chain is Valid
@app.route('/chain_valid', methods = ['GET'])
def chain_valid():
    
   # response = {'is_chain_valid': blockchain.is_chain_valid(blockchain.chain)}
    is_chain_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_chain_valid:
        response = {'message': 'Blockchain is VALID'}
    else:
        response = {'message': 'Current Blockchain is NOT VALID, Wait for the Consensus to be applied'}
   
    return jsonify(response), 200

#posting a transaction
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys =['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'Your transaction will be added to block with index {index}'}
    return jsonify(response), 201

#Decentralizing the Blockchain
#Connecting a new Node
    
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get("nodes")
    if nodes is None:
        return "There is no node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All nodes have been connected to the Jaycoin Network. Jaycoin Network now has the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201
    

#Replace chain with the longest
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    chain_replaced = blockchain.replace_chain()
    if chain_replaced:
        response = {'message': 'Blockchain is replace with the longest chain',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'This chain is currently the longest, so it was not replaced.',
                    'current_chain': blockchain.chain}
   
    return jsonify(response), 200

#Running the app
app.run(host = '0.0.0.0', port = 5000)
#http://127.0.0.1:5000/get_chain





    
    
    
    

    
    