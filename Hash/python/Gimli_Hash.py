#!/usr/bin/env python3

from hacspec.speclib import *
from Gimli import gimli

state = array_t(uint32_t, 12)
rate: nat_t = 16


@typechecked
def absorb_block(input_block: vlbytes_t, s: state) -> state:
    s[0] ^= bytes.to_uint32_le(input_block[0:4])
    s[1] ^= bytes.to_uint32_le(input_block[4:8])
    s[2] ^= bytes.to_uint32_le(input_block[8:12])
    s[3] ^= bytes.to_uint32_le(input_block[12:16])
    s = gimli(s)
    
    return s


@typechecked
def squeeze_block(s: state) -> bytes_t:
    block: bytes_t = array.create(rate, uint8(0))
    for i in range(4):
        block[4*i:4*(i + 1)] = bytes.from_uint32_le(s[i])

    return block


@typechecked
def gimli_hash(bytes_masukan: vlbytes_t, panjang_input: int) -> bytes_t:
    s: state = array.create(rate, uint32(0))
    num_full_block: int = panjang_input // rate
    for i in range(num_full_block):
        block_masukan: bytes_t = bytes_masukan[rate*i: rate*(i + 1)]
        s = absorb_block(block_masukan, s)

    bytes_sisa: int = panjang_input % rate
    block_terakhir = array.create(rate, uint8(0))
    block_terakhir[0: bytes_sisa] = bytes_masukan[(panjang_input - bytes_sisa): panjang_input]
    block_terakhir[bytes_sisa] = uint8(1)
    s[11] ^= uint32(0x01000000)
    s = absorb_block(block_terakhir, s)

    hasil: bytes_t = array.create(32, uint8(0))
    hasil[0:rate] = squeeze_block(s)
    s = gimli(s)
    hasil[rate:2*rate] = squeeze_block(s)

    return hasil


@typechecked
def hashing(_string: str):
    length = len(_string)
    block_message = array_t(uint8_t, length)
    state_input = block_message([uint8(i) for i in [ord(c) for c in _string]])
    out = gimli_hash(state_input, length)
    hasil = bytes.to_hex(out)
    return hasil