#!/usr/bin/python3.6
import sys
import inspect
import importlib
from Crypto.Cipher import AES
from Crypto.Random import random

class Player():
    def __init__(self):
        pass

    def popen(self, txt):
        '''
        A sophisticated print function that grabs texts from pointed to files and prints them
        returns the number of options if available
        '''
        txt += '.txt'
        with open(txt, 'r') as file:
            if '#' in txt:
                it = [x.split(';') for x in file.readlines()]
                it = [(y, float(x)) for x, y in it]
                [self.delay_print(*x) for x in it]
            else:
                text = file.read()
                print(text)
                if '____________________' in text:
                    return len(text.split('____________________')[1].split('\n')) - 2

    def delay_print(self, s, t=0.05):
        '''
        This is a utility function that facilitates stream-of-thought-like text presentation
        '''
        for c in s:
            sys.stdout.write('%s' % c)
            sys.stdout.flush()
            time.sleep(t)
        print()

    def choice(self, text):
        '''
        Prompts the user for a text file wlisting choices
        '''
        num = self.popen(text)
        while True:
            try:
                ans = input('Choice?: ')
                assert ans.isdigit(), "This answer is not a digit"
                ans = int(ans) - 1
                assert ans <= num, "This answer is not an option available"

                break
            except Exception as ex:
                print("Your answers was unacceptable as %s\nPlease try again" %
                      (ex))
        return ans

    def clear(self):
        print(chr(27) + "[2J")


class Puck(Player):
    def __init__(self):
        self.name = "Puck"

    def _take_(self, file):
        self.file = file

    def _learn_(self):
        try:
            c = importlib.import_module(self.file[:-3] + ".Book")
            l = inspect.getmembers(c, predicate=inspect.ismethod)
            self.delay_print("Ah yes here's what's inside")
            return [filter(lambda x: x[0][0] != '_')]
        except ModuleNotFoundError as mod:
            self.delay_print("I'm sorry I cant read this")

    def anon(self):
        key, iv = '4JB390Y3DDNYVA7S', 'K0GIE86G853QG2X5'
        obj = AES.new(key, AES.MODE_CBC, iv)
        return obj.encrypt(v)

    def denon(self):
        key, iv = '4JB390Y3DDNYVA7S', 'K0GIE86G853QG2X5'
        obj2 = AES.new(key, AES.MODE_CBC, iv)
        return obj2.decrypt(self.content)

