#Created October 11, 2024
#Last Edited September 14, 2025
#Nathaniel Puckett

import numpy as np

ALPHABET = {'A' : 7.9, 'B' : 1.4, 'C' : 2.7, 'D' : 4.1, 'E' : 12.2, 'F' : 2.1,
            'G' : 1.9, 'H' : 5.9, 'I' : 6.8, 'J' : 0.2,  'K' : 0.8, 'L' : 3.9,
            'M' : 2.3, 'N' : 6.5, 'O' : 7.2, 'P' : 1.8, 'Q' : 0.1, 'R' : 5.8,
            'S' : 6.1, 'T' : 8.8,  'U' : 2.7, 'V' : 1.0, 'W' : 2.3, 'X' : 0.2,
            'Y' : 1.9, 'Z' : 1.0}

BIGRAMS = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ES', 'ON', 'ST']

TRIGRAMS = ['THE', 'AND', 'ING', 'ENT', 'ION', 'HER', 'FOR', 'THA']

def frequency_analysis(text:str):
    frequencies = dict()
    bigrams = dict()
    trigrams = dict()
    text = text.upper()

    for i in range(len(text)):
        char = text[i]
        bi_char = text[i:i+2] if i < len(text) else ''
        tri_char = text[i:i+3] if i < len(text)-1 else ''

        if char.isalpha():
            if char in frequencies:
                frequencies[char] += 1
            else:
                frequencies[char] = 1

        if bi_char.isalpha():
            if bi_char in bigrams:
                bigrams[bi_char] += 1
            else:
                bigrams[bi_char] = 1
            
        if tri_char.isalpha():
            if tri_char in trigrams:
                trigrams[tri_char] += 1
            else:
                trigrams[tri_char] = 1
            
    frequencies = {ch : round((val / sum(frequencies.values())) * 100, 2) for ch, val in frequencies.items()}
    bigrams = {ch : val for ch, val in bigrams.items()}
    trigrams = {ch : val for ch, val in trigrams.items()}
    return frequencies, bigrams, trigrams


def shift(mode:str, text:str, s:int):
    message = str()
    text = text.lower()
    s = s * (1 if mode == 'e' else -1)

    for char in text:
        x = ord(char) - 97
        e_char = (x + s) % 26
        message += chr(e_char + 97)
    return message


def fa_shift(text:str, num_search:int): #uses frequency analysis on shift
    messages = str()

    frequencies = [[ch, val] for ch, val in frequency_analysis(text)[0].items()]
    frequencies.sort(key = lambda x: x[1], reverse = True)

    alphabet = [[ch, val] for ch, val in ALPHABET.items()]
    alphabet.sort(key = lambda x: x[1], reverse = True)

    for frequency in frequencies[:num_search]:
        s = (ord(frequency[0]) - ord(alphabet[0][0])) % 26
        messages += '\n'
        messages += f'Shifted {str(s)} (A = {shift('e', 'A', s).upper()})'
        messages += '\n' + shift('d', text, s) + '\n'
    return messages


def affine(mode:str, text:str, a:int, b:int):
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


def vigenere(mode:str, text:str, key:str):
    message = str()
    text = text.lower()
    key_vals = [ord(char) - 97 for char in key]

    for i in range(len(text)):
        x = ord(text[i]) - 97
        k = key_vals[i % len(key)] * (1 if mode == 'e' else -1)
        e_char = (x + k) % 26
        message += chr(e_char + 97)
    return message


def hill(mode:str, text:str, matrix):
    message = str()
    text = text.lower()
    m = len(matrix)

    if mode == 'd':
        det = int(round(np.linalg.det(matrix), 0))
        det_inv = pow(det, -1, 26)
        matrix = (np.linalg.inv(matrix) * det * det_inv) % 26
        print(matrix)

    for i in range(0, len(text), m):
        v_a = np.array([[ord(char) - 97] for char in text[i:i+m]])
        v_b = np.matmul(matrix, v_a)
        for b in v_b:
            message += chr(int(round(b[0], 0)) % 26 + 97)
    return message


def permutation(mode:str, text:str, ordering:list):
    message = str()
    text = text.lower()
    m = len(ordering)

    ordering_matrix = np.zeros([m, m])
    for i in range(m):
        ordering_matrix[ordering[i], i] = 1

    if mode == 'd':
        ordering_matrix = np.linalg.matrix_transpose(ordering_matrix)

    for i in range(0, len(text), m):
        v_a = np.array([[ord(char) - 97] for char in text[i:i+m]])
        print(v_a)
        print(ordering_matrix)
        v_b = np.matmul(ordering_matrix, v_a)
        for b in v_b:
            message += chr(int(round(b[0], 0)) % 26 + 97)
    return message


def autokey(mode:str, text:str, key:int):
    message = str()
    text = text.lower()
    s = key

    for char in text: 
        x = ord(char) - 97
        e_char = x + (s if mode == 'e' else -s)
        message += chr(e_char%26 + 97)
        s = (x if mode == 'e' else e_char%26)
    return message


def bf_autokey(text:str): #uses brute force on autokey
    messages = str()
    text = text.lower()

    for key in [ord(a[0].lower())-97 for a in ALPHABET]:
        attempt = autokey('d', text, key)
        messages += '\n'
        messages += f'{str(key)} : {attempt}'
        messages += '\n'
    return messages


#----------------------------[Testing]---------------------------
t_shift, t_affine, t_vigenere, t_hill, t_permutation = False, False, False, False, False
t_autokey = True

if t_shift:
    plaintext = "herewehavealongerstringtotestfrequencyanalysis"
    s = 16

    ciphertext = shift('e', plaintext, s)
    print('Shift')
    print(ciphertext)
    print(shift('d', ciphertext, s))
    print()

    print(fa_shift(ciphertext, 3))

#----------------------------------------

if t_affine:
    plaintext = "thisisateststring"
    a, b = 3, 10

    print('Affine')
    ciphertext = affine('e', plaintext, a, b)
    print(ciphertext)
    print(affine('d', ciphertext, a, b))
    print()

#-----------------------------------------

if t_vigenere:
    plaintext = "thisisateststring"
    key = "test"

    print('Vigenere')
    ciphertext = vigenere('e', plaintext, key)
    print(ciphertext)
    print(vigenere('d', ciphertext, key))
    print()

#-----------------------------------------

if t_hill:
    plaintext = "thisisateststringg"
    matrix = np.array([[1, 2], [2, 3]])

    print('Hill')
    ciphertext = hill('e', plaintext, matrix)
    print(ciphertext)
    print(hill('d', ciphertext, matrix))
    print()

#-----------------------------------------

if t_permutation:
    plaintext = "thisisateststringg"
    matrix = np.array([5, 4, 3, 2, 1, 0])

    print('Permutation')
    ciphertext = permutation('e', plaintext, matrix)
    print(ciphertext)
    print(permutation('d', ciphertext, matrix))
    print()

#-----------------------------------------

if t_autokey:
    plaintext = "thisisateststring"
    key = 8

    print('Autokey')
    ciphertext = autokey('e', plaintext, key)
    print(plaintext)
    print(ciphertext)
    print(autokey('d', ciphertext, key))
    print()