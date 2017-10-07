#  -*- coding: utf-8 -*-
import xml.sax
import xml.etree.ElementTree as ET
import re
import pickle
from operator import itemgetter
import sys
import codecs



def search_tree(s, top=10):
    if(os.path.isfile('trees/'+s[0]+'.tree') == True):
        file = open('trees/'+s[0]+'.tree', 'rb+')
        tree = pickle.load(file)
        file.close()
        return search_helper(s[1:], tree, top)
    else:
        return "Not found"

def search_helper(s, tree, top):
    if (len(s) < 1):
        print('Invalid search string')
        return {}
    if (len(s) == 1):
        return tree[s]['nodes'].items()[0:top-1]
    else:
        return {} if s[0] not in tree.keys() else search_helper(s[1:], tree[s[0]], top)


