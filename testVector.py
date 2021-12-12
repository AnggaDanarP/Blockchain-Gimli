from Gimli_Hash import gimli_hash
from hacspec.speclib import *

testVector = "Speak words we can all understand!"

def hashing(_string: str):
    a = [ord(c) for c in _string]
    length = len(_string)
    print(length)
    block_message = array_t(uint8_t, length)
    state_input = block_message([uint8(i) for i in a])
    print("state: ", state_input)
    out = gimli_hash(state_input, length)
    hasil = bytes.to_hex(out)
    return hasil

print(hashing(testVector))