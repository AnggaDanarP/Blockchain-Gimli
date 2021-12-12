# Blockchain

# install Flask : pip install Flask==0.12.2
# install Postman HTTP Client

# import

#from uuid import uuid4
#from urllib.parse import urlparse
#import requests

#import sys
import datetime
#import hashlib
import json
#from u_quark import digest
#from d_quark import digest
import pathlib
from MerkleTree import root_tree
from ecdsa import SECP256k1, VerifyingKey

#=======PENGUJIAN===========
import time
from Gimli_Hash import hashing
#from d_quark import digest
#from s_quark import digest
#from c_quark import digest
#import hashlib
#==========================

import codecs


from flask import Flask, jsonify, request
import requests
#from uuid import uuid4
#from urllib.parse import urlparse

# Building Blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transaction = [] #mempools
        self.nodes_file = "nodes.json"
        self.nodes = {} #empty set
        self.url_address = "127.0.0.1:5002"
        print(self.read_node())
        network = self.read_node()
        self.file_check()
        self.proof = 1
        self.previous_hash = '0'
        if network == []:
            print("buat block baru")
            self.create_block(self.previous_hash)
        else:
            print("replace block baru")
            self.replace_chain()
    
    def read_node(self):
        file_read = open(self.nodes_file, "r")
        file_read.seek(0)
        data = file_read.read()
        file_read.close()

        json_file = json.loads(data)
        return json_file["nodes"]
    
    def tx_validation(self, input_):
        
        json_input = input_
        public_key = json_input[0]['sender_public_key']
        signature =  json_input[0]['signature']
        prev_tx = json_input[0]['previous_tx']
        #print(input_)
        #print(signature)
        
        vk_byte = codecs.decode(public_key, 'hex')
        vk = VerifyingKey.from_string(vk_byte, curve=SECP256k1)
        
        signature_byte = codecs.decode(signature, 'hex')
        prev_tx_byte = prev_tx.encode('utf-8')
        check_sig = vk.verify(signature_byte,prev_tx_byte)
        
        return check_sig
    
        
    def create_block(self, previous_hash):
        if self.transaction == []:
            block = {
                    'index' : len(self.chain) + 1,
                    'timestamp' : datetime.datetime.now(),
                    'proof' : self.proof,
                    'previous_hash' : previous_hash,
                    'merkle_root' : "0",
                    'transaction' : self.transaction}
            output = self.proof_of_work(block)
            block['proof'] = output['proof']
            block['hash'] = output['hash']
            self.transaction = []
            self.chain.append(block)
        else:
            block = {
                    'index' : len(self.chain) + 1,
                    'timestamp' : datetime.datetime.now(),
                    'proof' : self.proof,
                    'previous_hash' : previous_hash,
                    'merkle_root' : root_tree(self.transaction),
                    'transaction' : self.transaction}
            output = self.proof_of_work(block)
            block['proof'] = output['proof']
            block['hash'] = output['hash']
            self.transaction = []
            self.chain.append(block)
            network = self.read_node()
            for nodes in network:
                requests.get(f'http://{nodes}/replace_chain')
        return block
    
    def  get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, mine_block):
        proof = 1
        check_proof = False
        output = {}
        while check_proof is False:
            mine_block['proof'] = proof
            hash_operation = self.hash(mine_block)
            if hash_operation[:1] == '0':
            #if hash_operation[:4] == '0000' :
                #hash_previous_block = hash_operation
                output['hash'] = hash_operation
                output['proof'] = proof
                #self.block['hash'] = hash_operation
                print("Hasil nonce = ",proof)
                print("Hasil hash=",hash_operation)
                check_proof = True
            else : 
                print("Nonce = ",proof)
                print("hash from ^ nonce = ",hash_operation)
                proof += 1
        return output
    
    def hash(self, block):
        #encoded_block = json.dumps(block, sort_keys = True, default = str).encode()
        encoded_block1 = json.dumps(block, sort_keys = True, default = str)

        #return hashlib.sha256(encoded_block).hexdigest()
        return hashing(encoded_block1)
    
    
    def add_transaction(self, sender, receiver, hash_):
        self.transaction.append({'input' : sender ,
                                 'output' : receiver,
                                 'hash' : hash_})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    
# =============================================================================
#     def add_node(self, address):
#         parsed_url = urlparse(address)
#         self.nodes.add(parsed_url.netloc) #add sama seperti append, namun set kosong tidak punya fungsi append
# =============================================================================
        
    def replace_chain(self):
        network = self.read_node()
        longest_chain = None
        max_length = len(self.chain) #max length dari nodes ini
        
        for nodes in network:
            #print("NODES + ", nodes)
            if nodes == self.url_address:
                length = max_length
                chain = self.chain
            else:
                response = requests.get(f'http://{nodes}/get_chain')
                #kunci buat segala permasalahan
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']
            if length > max_length: #and self.is_chain_valid(chain)
                max_length = length
                longest_chain = chain
        if longest_chain: #sama seperti if longest chain not None
            self.chain = longest_chain
            return True
        return False
                    
    def distributed_transaction(self):#distributed mempool
        network = self.read_node()
        
        for nodes in network:
            response1 = requests.get(f'http://{nodes}/check_transaction')
            #response2 = requests.get(f'http://{nodes}/get_chain')
            if response1.status_code == 200:
                transaction = response1.json()['transaction']
                self.transaction = transaction
                return True
                #length = response2.json()['length']
                #if length == new_block:
                #    #max_transaction = transaction
                #    self.transaction = []
                #    return True
                #else:
                #    self.transaction = transaction
                #    return True
            
        return False
    
    def file_check(self):
        #nodes_file = "nodes.json"

        file = pathlib.Path(self.nodes_file)
        if file.exists():    
            file_read = open(self.nodes_file, "r")
            file_read.seek(0)
            data = file_read.read()
            file_read.close()

            json_file = json.loads(data)
    
            self.nodes.update(json_file)
            #requests.get(url_address+"/replace_chain")   
            print(self.nodes)
            print("File Exist")
            
            self.replace_chain()

            json_file["nodes"].append(self.url_address)

            file_write = open(self.nodes_file, "w")
            json_write = file_write.write(json.dumps(json_file))
            file_write.close()
    
        else:
            f = open(self.nodes_file, "w+")
            wallet_tx = {"nodes" : [self.url_address]}
            f.write(json.dumps(wallet_tx))
            f.close()
            
                    
    
# Mining Blockchain
        
# 1. creating web app
app = Flask(__name__)        

#creating an address on port 5000
#node_address = str(uuid4()).replace('-', '')
    
# 2. creating blockchain
blockchain = Blockchain()

# 3. mining new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    start_time = time.time()
    previous_block = blockchain.get_previous_block()
    previous_hash = previous_block['hash']
    block = blockchain.create_block(previous_hash)
    end_time = time.time()
    processing_time = end_time - start_time
    
    response = {
                'messages' : 'Congratulation you just mined a block',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transaction' : block['transaction'],
                'hashing_time' : processing_time
                }
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain' : blockchain.chain, 
                'length' : len(blockchain.chain)
                }
    return jsonify(response), 200


# adding transcation to mempool
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['input', 'output', 'hash']
    if not all(key in json for key in transaction_keys):
        return 'Lengkapi data yang dibutuhkan', 400
    
    validation = blockchain.tx_validation(json['input'])
    if validation:
        index = blockchain.add_transaction(json['input'], json['output'], json['hash'])
        response = {'messages' : f'transaction akan dimasukkan ke dalam block ke {index}'}
        return jsonify(response), 201
    else:
        index = blockchain.add_transaction(json['input'], json['output'], json['hash'])
        response = {'messages' : 'Transaksi di gagalkan'}
        return jsonify(response), 403
    
    
    


# decentralising blockhain
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No Node', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'messages' : 'All the node are connected', 
                'total_nodes' : list(blockchain.nodes) 
                    }
    return jsonify(response), 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    replace_chain = blockchain.replace_chain()
    blockchain.transaction = []
    if replace_chain: # TRUE
        response = {'messages' : 'Chain replaced',
                    'new chain' : blockchain.chain}
    else: # FALSE
        response = {'messages' : 'Chain not replaced',
                    'chain' : blockchain.chain}
    return jsonify(response), 200

@app.route('/distributed_mempool', methods = ['GET'])
def distributed_mempool():
    distributed_mempool = blockchain.distributed_transaction()
    if distributed_mempool: # TRUE
        response = {'messages' : 'Mempool updated',
                    'new chain' : blockchain.transaction}
    else: # FALSE
        response = {'messages' : 'Mempool not updated',
                    'chain' : blockchain.transaction}
    return jsonify(response), 200


@app.route('/check_nodes', methods = ['GET'])
def check_nodes():
    checking = blockchain.read_node()
    #response = {'nodes' : checking}
    return jsonify(checking), 200

@app.route('/check_transaction', methods = ['GET'])
def check_transaction():
    check_mempool = blockchain.transaction
    response = {'transaction' : check_mempool}
    return jsonify(response), 200

@app.route('/quit_network', methods = ['GET'])
def quit_network():
    #print("hallo lagi")
    file_read = open(blockchain.nodes_file, "r")
    file_read.seek(0)
    data = file_read.read()
    file_read.close()

    json_file = json.loads(data)
    
    json_file["nodes"].remove(blockchain.url_address)
    #print("hallo")
    
    blockchain.nodes.update(json_file)
    #print("HELLOOOO", blockchain.nodes)
    #blockchain.replace_chain()

    file_write = open(blockchain.nodes_file, "w")
    json_write = file_write.write(json.dumps(json_file))
    file_write.close()
    
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown:
        shutdown()
    response = {'message' : "Telah berpisah dari Network"}
    return response



# running the application
app.run(host = '0.0.0.0', port = 5002)
















