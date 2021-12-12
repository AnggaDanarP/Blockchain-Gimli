#!/usr/bin/env python3

from hacspec.speclib import *

state = array_t(uint32_t, 12)

@typechecked
def gimli_round(input : state, putaran : int) -> state:
    # SP-box
    for kolom in range(4):
        x : uint32_t = uintn.rotate_left(input[kolom], 24)
        y : uint32_t = uintn.rotate_left(input[kolom + 4], 9)
        z : uint32_t = input[kolom + 8]

        input[kolom + 8] = x ^ (z << 1) ^ ((y & z) << 2)
        input[kolom + 4] = y ^ x ^ ((x | z) << 1)
        input[kolom] = z ^ y ^ ((x & y) << 3)
    
    # Small-Swap
    if ((putaran & 3) == 0):
        input[0], input[1] = input[1], input[0]
        input[2], input[3] = input[3], input[2]
    
    # Big-Swap
    if ((putaran & 3) == 2):
        input[0], input[2] = input[2], input[0]
        input[1], input[3] = input[3], input[1]
    
    # Add-Constant
    if ((putaran & 3) == 0):
        input[0] = input[0] ^  (uint32(0x9e377900) | uint32(putaran))
    
    return input

@typechecked
def gimli(masukan : state) -> state:
    template : state = array.copy(masukan)
    for round in range(24):
        template = gimli_round(masukan, 24 - round)
    return template        
