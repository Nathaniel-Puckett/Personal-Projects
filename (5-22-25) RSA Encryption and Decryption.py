import math
import montecarlo
import numpy as np

def str_to_bin(text):

    bin_list = list()
    for char in text:
        char_bs = format(ord(char), 'b')
        for i in range(8-len(char_bs)):
            bin_list.append(0)
        for bit in char_bs:
            bin_list.append(bit)

    text_bs = montecarlo.BitString(0)
    text_bs.set_config(bin_list)

    return text_bs

def bin_to_str(in_bs):

    bit_array = in_bs.config()
    temp_bs = montecarlo.BitString(8)
    message = ''

    for i in range(len(bit_array)//8):
        char_bits = bit_array[(i*8):((i+1)*8)]
        temp_bs.set_config(char_bits)
        char = chr(temp_bs.integer())
        message += char

    return message

def encryptRSA(message, N, c):

    if isinstance(message, str):
        msg_bs = str_to_bin(message)
        unenc_msg = int(msg_bs.integer())
    else:
        unenc_msg = message

    return (unenc_msg**c)%N

def decryptRSA(message, p, q, c):

    lcm = int(((p-1)*(q-1))/math.gcd(p-1, q-1))
    d = pow(c, -1, lcm)

    return (message**d)%(p*q)
    

p, q = 941, 9949
N = p*q
lcm = int(((p-1)*(q-1))/math.gcd(p-1, q-1))

'''
coprimes = list()
for i in range(1, lcm):
    if math.gcd(i, lcm) == 1:
        coprimes.append(i)

print(coprimes)
'''

c = 17
msg = 'bye'

enc_msg = encryptRSA(msg, N, c)
print('Encrypted Message :', enc_msg)

decr_msg = decryptRSA(enc_msg, p, q, c)
print('Decrypted Message :', decr_msg)

test_bs = montecarlo.BitString(8*len(msg))
test_bs.set_integer_config(decr_msg)

print('Plaintext Message :', bin_to_str(test_bs))