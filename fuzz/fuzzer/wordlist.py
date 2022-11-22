import os, sys

class WordlistFuzzer:
    def __init__(self, wordlist_fp):
        self.words = wordlist_fp.readlines()


