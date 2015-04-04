# -*- coding: utf-8 -*-

import codecs
import doctest
import collections
import re


class wordlist(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys
        self.rx = r"(\S+)\s*=\s*(.+)"

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def parseline(self, line):
        x = re.match(self.rx, line.strip())
        if x:
            self.store[x.group(1)] = x.group(2)

    def parse(self, txt):
        for line in txt.split('\n'):
            self.parseline(line)

    def load(self, filename):
        with codecs.open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            self.parseline(line)

    def save(self, filename):
        with codecs.open(filename, "w", encoding="utf-8") as f:
            for w in sorted(self.store.keys(), key=lambda s: s.lower()):
                f.write(w + ' = ' + self.store[w] + "\n")



# -----------------------------------------------

if __name__ == '__main__':

    print(doctest.testmod())



