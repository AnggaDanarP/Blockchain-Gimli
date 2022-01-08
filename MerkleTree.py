#importing
from collections import OrderedDict
import hash
import json

#Dekalrasi kelas
class Merkle_tree:
    
    #deklarasi kelas object
    def __init__(self, listoftransaction=None):
        self.listoftransaction = listoftransaction
        self.past_transaction = OrderedDict()
    
    #create MerkleTree
    def create_tree(self):
        
        #continue of declaration
        listoftransaction = self.listoftransaction
        past_transaction = self.past_transaction
        temp_transaction = []
        
        for index in range(0,len(listoftransaction),2):
            
            #get the most left element
            current = listoftransaction[index]
            
            #if there is still index left get the right of the left most element
            if index+1 != len(listoftransaction):
                current_right = listoftransaction[index+1]
                
            #if reach the limit of the list then make an empty string
            else:
                current_right = ''
                
            #apply the hash value to current hash
            current_hash = hash.gimli(current).replace(" ", "") #using SHA-256
            
            #if the current right hash is not an empty string ''
            if current_right != '':
                current_right_hash = hash.gimli(current_right).replace(" ", "") #using SHA-256
                
            #add transaction to the dictionary
            past_transaction[listoftransaction[index]] = current_hash
            
            #if the next right is empty
            if current_right != '' :
                past_transaction[listoftransaction[index+1]] = current_right_hash
            
            #create new list of trasanction
            if current_right != '' :
                temp_transaction.append(current_hash + current_right_hash)
            
            #if the left most is an empty then only add the current value
            else:
                temp_transaction.append(current_hash)
                
        #update the variable and rerun the function
        if len(listoftransaction) != 1 :
            self.listoftransaction = temp_transaction
            self.past_transaction = past_transaction
            
            #run the function again until got the root
            self.create_tree()
            
# =============================================================================
#     def get_past_transaction(self):
#         past_transaction = self.past_transaction
#         #print(list(self.past_transaction.keys()))
#        # print(type(self.past_transaction))
#         return past_transaction
# =============================================================================
    
    def get_root_leaf(self):
        last_key = self.past_transaction.keys()#[-1]
        #print(type(self.past_transaction))
        list_last_key = list(last_key)[-1]
        #print("last key = ", list_last_key)
        return self.past_transaction[list_last_key]



def root_tree(input_):
    #craete the new class
    MT = Merkle_tree()
    
    #list of transaction
    transaction = []
    for i in input_:
        transaction_list = str(i)
        transaction.append(transaction_list)
        
    #pass on the trasaction list
    MT.listoftransaction = transaction
    
    #create the merkle tree transaction
    MT.create_tree()
    
    #retrieve the transaction
   # past_transaction = MT.past_transaction
    
    return MT.get_root_leaf()


def leaf_tree(input_):
    
    MT = Merkle_tree()
    
    #list of transaction
    transaction = []
    for i in input_:
        transaction_list = str(i)
        transaction.append(transaction_list)
        
    #pass on the trasaction list
    MT.listoftransaction = transaction
    
    #create the merkle tree transaction
    MT.create_tree()
    
    #retrieve the transaction
    past_transaction = MT.past_transaction
    
    return json.dumps(past_transaction, indent=4)
    
    
            
#declare the main part of the function
# =============================================================================
# if __name__ == "__main__":
#     
#     #craete the new class
#     MT = Merkle_tree()
#     
#     #list of transaction
#     string_transaction = []
#     transaction = [{
#  "sender" : "aaa",
#  "receiver" : "bbb",
#  "amount" : 20
#  }, {
#  "sender" : "aaa",
#  "receiver" : "ccc",
#  "amount" : 20
#  }, {
#  "sender" : "aaa",
#  "receiver" : "ddd",
#  "amount" : 20
#  }, {
#  "sender" : "aaa",
#  "receiver" : "eee",
#  "amount" : 20
#  }]
#     for i in transaction : 
#         transaction_list = str(i)
#         string_transaction.append(transaction_list)
#     
#     #pass on the trasaction list
#     MT.listoftransaction = string_transaction
#     
#     #create the merkle tree transaction
#     MT.create_tree()
#     
#     #retrieve the transaction
#     past_transaction = MT.past_transaction
#     
#     #print(past_transaction)
#     #print(type(past_transaction))
#     
#     
#     #get the last transaction and print
#     print("First Example - Even number of transaction Merkel Tree")
#     print("Final root of the tree : ",MT.get_root_leaf())
#     print(json.dumps(past_transaction, indent=4))
#     print("-" * 50 )
#     
#     #second example
#     print("Second Example - Odd number of transaction Merkel Tree")
#     MT = Merkle_tree()
#     transaction = ['a', 'b', 'c', 'd', 'e']
#     MT.listoftransaction = transaction
#     MT.create_tree()
#     past_transaction = MT.past_transaction
#     print("Final root of the tree : ",MT.get_root_leaf())
#     print(json.dumps(past_transaction, indent=4))
#     print("-" * 50 )
#     
#     #actual usecase
#     print("Final Example - Actuall use case of the Merkle Tree")
#     
#     #decalre a trasaaction - ground truth
#     ground_truth_tree = Merkle_tree()
#     ground_truth_transaction = ['a', 'b', 'c', 'd', 'e']
#     ground_truth_tree.listoftransaction = ground_truth_transaction
#     ground_truth_tree.create_tree()
#     ground_truth_past_transaction = ground_truth_tree.past_transaction
#     ground_truth_root = ground_truth_tree.get_root_leaf()
#     
#     #decalre a tampered trasaaction 
#     tampered_tree = Merkle_tree()
#     tampered_transaction = ['a', 'b', 'c', 'd', 'f']
#     tampered_tree.listoftransaction = tampered_transaction
#     tampered_tree.create_tree()
#     tampered_past_transaction = tampered_tree.past_transaction
#     tampered_root = tampered_tree.get_root_leaf()
#     
#     #three company share all the transaction
#     print("Company A - my final transaction hash : ",ground_truth_root)
#     print("Company B - my final transaction hash : ",ground_truth_root)
#     print("Company C - my final transaction hash : ",tampered_root)
#     
#     #print out all the transaction
#     print("\n\nGround Truth past Transaction ")
#     print(json.dumps(ground_truth_past_transaction, indent=4))
#     
#     print("\n\nTamper Truth past Transaction ")
#     print(json.dumps(tampered_past_transaction, indent=4))
# =============================================================================
    
    
    
            
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
        
