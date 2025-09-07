#Created October 11, 2024
#Last Edited October 12, 2024
#Nathaniel Puckett

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
    
    
    
    
    
    
    

    
