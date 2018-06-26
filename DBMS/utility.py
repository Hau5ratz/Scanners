'''
\nThis is a utility module that just provides
Multi-utility scripts
'''
from tkinter import messagebox, filedialog

def check_string(base, sample):
    '''
    Checks if long string A
    is in string B
    by reducing A
    returns True if is the case
    '''
    assert all([isinstance(base, str), isinstance(sample, str)]
               ), 'Was given a non-string'
    copy = sample
    for x in range(1, len(sample)):
        copy = sample[x:-1 * x]
        if copy.count(' ') >= 3:
            if copy in base:
                return True
        else:
            return False

def get_select(selection):
    '''
    Takes a list
    challanges the user to make a selection from it
    returns the selection
    '''
    assert isinstance(selection, list), "List required!"
    string = "Please choose from the following:"
    c = 1
    for select in selection:
        string += '\n'
        string += '%s- %s' % (c, select)
        c += 1
    while True:
        ans = input(string + "\nPlease pick a number: ")
        if ans.isdigit():
            if int(ans) <= len(selection):
                return selection[int(ans) - 1]
            else:
                print("Out of range try again")
        else:
            print('Not a number try again')

def frequest(self, message=None):
    if message:
        messagebox.showinfo('File request', message)
    filepath = filedialog.askopenfilename()
    if filepath == '':
        messagebox.showwarning("Warning", "No File path specified")
    else:
        return filepath