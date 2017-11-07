def get_next_drive_name():
    range1 = 'b'
    range2 = 'z'    
    # Generates the characters from range1 to range2, inclusive
    def letter_range(range1,range2):
        for letter in range(ord(range1), ord(range2)+1):
            yield chr(letter)    
    
    string = ''       
    for letter in letter_range(range1,range2):
        seq = ('xvd',letter)
        print (string.join(seq))
               

get_next_drive_name()