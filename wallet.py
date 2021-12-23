from Gimli_Hash import hashing
from ecdsa import SigningKey, SECP256k1
import codecs
import hashlib
import json
import pathlib
import requests
from tkinter import filedialog
import numpy as np
from PIL import Image
#import skvideo.io

class Wallet:
    def __init__(self):
        self.private_key = "60cf347dbc59d31c1358c8e5cf5e45b822ab85b79cb32a9f3d98184779a9efc1"
        self.sk = SigningKey.from_string(codecs.decode(self.private_key, 'hex'), curve=SECP256k1)
        vk = self.sk.verifying_key #public key
        self.vk_toString = vk.to_string().hex()
        ripemd160 = hashlib.new('ripemd160') #calling ripemd160
        ripemd160.update(self.vk_toString.encode())
        self.encrypted_public_key = ripemd160.hexdigest() #encrypted public key
        self.previous_tx = "0"
        self.filename = "wallet.json"
        self.nodes_file = "nodes.json"
        self.file_check()

    def new(self, private_key, public_key, address):
        f = open(self.filename, "w+")
        wallet_tx = {"private_key" : private_key,
                     "public_key" : public_key,
                     "address" : address,
                     "transaction" : []}
        f.write(json.dumps(wallet_tx))
        f.close()
    
    def broadcast(self, transaction):
        file_read = open(self.nodes_file, "r")
        file_read.seek(0)
        data = file_read.read()
        file_read.close()
        json_file = json.loads(data)
        for nodes in json_file['nodes']:
            response = requests.post(f"http://{nodes}/add_transaction", json=transaction)
            print(response.text)
            print(f"{nodes, response}")
        return print("broadcast to mempool")
    
    def transaction(self, amount):
        input_address = input("masukkan address = ")
        byte_prev = self.previous_tx.encode()
        byte_signature = self.sk.sign(byte_prev)
        signature = byte_signature.hex()           
        tx = {
                'input' : [{'previous_tx' : self.previous_tx,
                        'index' : 000000, #nilai index ke berapa yang di ambil dr output transaksi sebelumnya
                        'size' : 0,
                        'signature' : signature, #signature dari private key dengan hash tx sebelumnya
                        'sender_public_key' : self.vk_toString,
                        'sequence' : 'ffffffff'}],
                'output' : [{'amount' : amount,
                            'receiver' : input_address,
                            'receiver_public_key' : self.vk_toString, }]}
        return tx
    
    def get_transaction(self):
        filename = filedialog.askopenfile(
            initialdir="/",
            title="Pilih Gambar",
            filetypes=(
                ("png files", "*.png"),
                ("jpg files", "*.jpg"),
                ("bmp files", "*.bmp"),
                ("All files", "*")
            )
        )
        image = filename.name
        amount = np.asarray(Image.open(image))
        #amount = skvideo.io.vread(image)
        return str(amount)
    
    def file_check(self):
        file = pathlib.Path(self.filename)
        if file.exists():   
            print("PUBLIC KEY = ", self.vk_toString)
            get_tx = self.get_transaction()
            print("POST TRANSACTION")
            file_read = open(self.filename, "r")
            file_read.seek(0)
            data = file_read.read()
            file_read.close()
            jsonfile = json.loads(data)
            tx = self.transaction(get_tx)
            json_tx = jsonfile["transaction"].append(tx)
            json_data = json.dumps(jsonfile["transaction"])
            file_write = open(self.filename, "w")
            file_write.write(json.dumps(jsonfile))
            file_write.close()
            self.broadcast(tx)
        else:
            self.new(self.private_key, self.vk_toString, self.encrypted_public_key)
            print("make new file")
            self.file_check()

wallet = Wallet()
