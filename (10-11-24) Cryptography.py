#Created October 11, 2024
#Last Edited September 8, 2025
#Nathaniel Puckett

import numpy as np

def Shift(mode:str, text:str, s:int):
    message = str()
    text = text.lower()
    s = s * (1 if mode == 'e' else -1)

    for char in text:
        x = ord(char) - 97
        e_char = (x + s) % 26
        message += chr(e_char + 97)
    return message


def Affine(mode:str, text:str, a:int, b:int):
    message = str()
    text = text.lower()

    try:
        a_i = pow(a, -1, 26)
    except:
        print("Invalid input for (a). (a) must be coprime with 26.")
        return None

    for char in text:
        x = ord(char) - 97
        if mode == 'e':
            e_char = (a*x + b) % 26
        elif mode == 'd':
            e_char = (a_i*(x - b)) % 26
        message += chr(e_char + 97)
    return message


def Vigenere(mode:str, text:str, key:str):
    message = str()
    text = text.lower()
    key_vals = [ord(char) - 97 for char in key]

    for i in range(len(text)):
        x = ord(text[i]) - 97
        k = key_vals[i % len(key)] * (1 if mode == 'e' else -1)
        e_char = (x + k) % 26
        message += chr(e_char + 97)
    return message

#Not functioning yet
def Hill(mode:str, text:str, matrix):
    message = str()
    text = text.lower()
    m = matrix.ndim

    if mode == 'd':
        det = int(round(np.linalg.det(matrix), 0))
        print(det)
        det_inv = pow(det, -1, 26)
        print(det_inv)
        matrix = (np.linalg.inv(matrix) * det * det_inv) % 26

    for i in range(0, len(text), m):
        v_a = np.array([ord(char) - 97 for char in text[i:i+m]])
        v_b = np.matmul(v_a, matrix)
        print(v_a, v_b)
        for b in v_b:
            message += chr(int(round(b, 0))%26 + 97)
    return message


#----------------------------[Testing]---------------------------

plaintext = "thisisateststring"
s = 16

ciphertext = Shift('e', plaintext, s)
print('Shift')
print(ciphertext)
print(Shift('d', ciphertext, s))
print()

#----------------------------------------

plaintext = "thisisateststring"
a, b = 3, 10

print('Affine')
ciphertext = Affine('e', plaintext, a, b)
print(ciphertext)
print(Affine('d', ciphertext, a, b))
print()

#-----------------------------------------

plaintext = "thisisateststring"
key = "test"

print('Vigenere')
ciphertext = Vigenere('e', plaintext, key)
print(ciphertext)
print(Vigenere('d', ciphertext, key))
print()

#-----------------------------------------

plaintext = "thisisateststrin"
matrix = np.array([[7, 1], [2, 1]])

print('Hill')
ciphertext = Hill('e', plaintext, matrix)
print(ciphertext)
print(Hill('d', ciphertext, matrix))

#----------------------------[Legacy Functions]---------------------------

"""
ALPHABET = [['A', 7.9], ['B', 1.4], ['C', 2.7], ['D', 4.1], ['E', 12.2], 
            ['F', 2.1], ['G', 1.9], ['H', 5.9], ['I', 6.8], ['J', 0.2], 
            ['K', 0.8], ['L', 3.9], ['M', 2.3], ['N', 6.5], ['O', 7.2], 
            ['P', 1.8], ['Q', 0.1], ['R', 5.8], ['S', 6.1], ['T', 8.8], 
            ['U', 2.7], ['V', 1.0], ['W', 2.3], ['X', 0.2], ['Y', 1.9], 
            ['Z', 1.0]]

def Sorting(word):
    return word[1]

SORTED_ALPHABET = ALPHABET[:]
SORTED_ALPHABET.sort(key = Sorting, reverse = True)
    
def Caesar(message, shift):
    message = message.lower()
    shift = (shift + 26) % 26
    encrypted_message = ''
    for char in message:
        ord_char = ord(char)
        if not 97 <= ord_char <= 122:
            pass
        elif ord_char + shift > 122:
            ord_char = 96 + ((ord_char + shift) - 122)
        elif ord_char + shift < 97:
            ord_char = 123 + ((ord_char + shift) - 97)
        else:
            ord_char += shift
        ord_char = chr(ord_char)
        encrypted_message += ord_char
    return encrypted_message

def Frequency(message, is_printed=False):
    message = message.lower()
    frequency_list = [0] * 26
    total = 0
    for char in message:
        if char.isalpha():
            ord_char = ord(char) - 97
            frequency_list[ord_char] += 1
            total += 1
    letter_frequencies = [0] * 26
    for i in range(len(frequency_list)):
        letter_frequencies[i] = [chr(int(i) + 97), round((frequency_list[i] / total) * 100, 2)]
    letter_frequencies.sort(reverse = True, key = Sorting)
    if is_printed:
        for pair in letter_frequencies:
            if pair[1] != 0:
                print(f'{pair[0].upper()} : {pair[1]}%')
    else:
        return letter_frequencies

def Uncaesar(message):
    top_frequencies = Frequency(message)[0:10]
    analyzed_messages = ''
    for frequency in top_frequencies:
        message_shift = (ord(SORTED_ALPHABET[0][0].lower()) - ord(frequency[0]))
        analyzed_messages += '\n'
        analyzed_messages += f'Shifted {str(-message_shift)} (A = {Caesar("A", -message_shift).upper()})'
        analyzed_messages += '\n' + Caesar(message, message_shift) + '\n'
    return analyzed_messages

encrypted_message = "BEEAKFYDJXUQYHYJIQRYHTYJIQFBQDUYJIIKFUHCQD"
print(Uncaesar(encrypted_message))
"""