from datetime import datetime
import json
import pathlib
import time
from MerkleTree import root_tree#, leaf_tree
from ecdsa import SECP256k1, VerifyingKey, BadSignatureError
import codecs
from flask import Flask, jsonify, request
import requests
#import hash
import hashlib

class Blockchain:
    def __init__(self):
        self.chain, self.transaction = [], []
        self.previous_hash = '00000000000000'
        self.nodes = {} #empty set
        self.url_address = "127.0.0.1:5001"
        self.file_check()
        if self.transaction == []:
            self.genesis_block()
        else :
            self.replace_chain()
        
    def open_file(self):
        nodes_file = "nodes.json"
        file_read = open(nodes_file, "r")
        file_read.seek(0)
        data = file_read.read()
        file_read.close()
        return json.loads(data)

    def read_node(self):
        json_file = self.open_file()
        return json_file["nodes"]
    
    def tx_validation(self, _input):
        public_key = _input[0]['sender_public_key']
        signature =  _input[0]['signature']
        prev_tx = _input[0]['previous_tx']
        
        vk_byte = codecs.decode(public_key, 'hex')
        vk = VerifyingKey.from_string(vk_byte, curve=SECP256k1)
        
        signature_byte = codecs.decode(signature, 'hex')
        prev_tx_byte = prev_tx.encode('utf-8')
        check_sig = vk.verify(signature_byte,prev_tx_byte)
        
        return check_sig
    
    def genesis_block(self):
        transaction = [{
                'hash' : '',
                'version': '1',
                'input count' : '01000000',
                'input' : [{
                        'hash' : '',
                        'previous transaction' : self.previous_hash,
                        'index' : 000000,
                        'scriptSig size' : '0',
                        'signature' : '04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73', 
                        'sender_public_key' : '',
                        'sequence' : 'FFFFFFFF'}],
                'output count' : 0,
                'output' : [{'amount' : '',
                            'scriptPublicKey size' : '0',
                            'scriptPublicKey' : '4104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac'}],
                'lock time' : 0}]
        block = {
                'index' : len(self.chain) + 1,
                'previous_hash' : self.previous_hash,
                'timestamp' : int(time.time()),
                'difficulty': '0000',
                'nonce' : 0,
                'merkle_root' : root_tree(transaction),
                'transaction' : transaction}
        output = self.proof_of_work(block)
        block['nonce'] = output['nonce']
        block['hash'] = output['hash']
        self.transaction = []
        self.chain.append(block)
        return block
        
    def create_block(self, previous_hash):
        block = {
                'index' : len(self.chain) + 1,
                'previous_hash' : previous_hash,
                'timestamp' : int(time.time()),
                'difficulty': '0000',
                'nonce' :0,
                'merkle_root' : root_tree(self.transaction),
                'transaction' : self.transaction}
        output = self.proof_of_work(block)
        block['nonce'] = output['nonce']
        block['hash'] = output['hash']
        self.transaction = []
        self.chain.append(block)
        network = self.read_node()
        for nodes in network:
            requests.get(f'http://{nodes}/replace_chain')
        return block
    
    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, mine_block):
        proof = 1
        check_proof = False
        output = {}
        start_time = time.time()
        while check_proof is False:
            mine_block['nonce'] = proof
            hash_operation = self.hash(mine_block)
            if hash_operation[:4] == '0000':
                output['hash'] = hash_operation
                output['nonce'] = proof
                check_proof = True
            print("Nonce = ",proof)
            print("hash from ^ nonce = ",hash_operation)
            proof += 1
        end_time = time.time()
        result = end_time - start_time
        print("Time to mine block = ",int(round(result * 1000)),"ms")
        return output
    
    def hash(self, block):
        #encoded_block = json.dumps(block, sort_keys = True, default = str)
        #return hash.gimli(encoded_block).replace(" ", "")
        encoded_block = json.dumps(block, sort_keys = True, default = str).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def add_transaction(self, sender, receiver):
        self.transaction.append({'version': '01000000',
                                 'input count' : 0,
                                 'input' : sender ,
                                 'output count' : 0,
                                 'output' : receiver,
                                 'lock time' : '00000000'})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
        
    def replace_chain(self):
        network = self.read_node()
        longest_chain = None
        max_length = len(self.chain) #max length dari nodes ini
        
        for nodes in network:
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
                #length = response2.json()['length']
                self.transaction = transaction
                return True
            
        return False
    
    def file_check(self):
        nodes_file = "nodes.json"

        file = pathlib.Path(nodes_file)
        if file.exists():    
            json_file = self.open_file()
    
            self.nodes.update(json_file)
            #requests.get(url_address+"/replace_chain")   
            print("File Exist")
            
            self.replace_chain()

            json_file["nodes"].append(self.url_address)

            file_write = open(nodes_file, "w")
            json_write = file_write.write(json.dumps(json_file))
            file_write.close()
    
        else:
            print("make a node file .json")
            f = open(nodes_file, "w+")
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
    print("Get the previous block...")
    previous_block = blockchain.get_previous_block()
    previous_hash = previous_block['hash']
    print("Start Mining")
    block = blockchain.create_block(previous_hash)
    end_time = time.time()
    processing_time = end_time - start_time
    
    response = {
                'messages' : 'Congratulation you just mined a block',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'nonce' : block['nonce'],
                'previous_hash' : block['previous_hash'],
                'transaction' : block['transaction'],
                'hashing_time' : processing_time
                }
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
                'chain' : blockchain.chain, 
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
    try:
        blockchain.tx_validation(json['input'])
        index = blockchain.add_transaction(json['input'], json['output'])
        response = {'messages' : f'transaction akan dimasukkan ke dalam block ke {index}'}
        return jsonify(response), 201
    except BadSignatureError:
        response = {'messages' : 'Transaksi di gagalkan'}
        return jsonify(response), 403

# decentralising blockhain
@app.route('/connect_node', methods = ['POST']) #akan dihapus
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

@app.route('/replace_chain', methods = ['GET']) #akan dihapus
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
    response = {'transaction' : blockchain.transaction}
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

app.run(host = '0.0.0.0', port = 5001)


@app.errorhandler(Exception)
def error_handle():
    print("hallo lagi")
    file_read = open(blockchain.nodes_file, "r")
    file_read.seek(0)
    data = file_read.read()
    file_read.close()

    json_file = json.loads(data)
    
    blockchain.nodes.update(json_file)
    #print("HELLOOOO", blockchain.nodes)
    blockchain.replace_chain()

    json_file["nodes"].remove(blockchain.url_address)
    print("hallo")

    file_write = open(blockchain.nodes_file, "w")
    json_write = file_write.write(json.dumps(json_file))
    file_write.close()