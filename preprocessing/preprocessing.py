#  -*- coding: utf-8 -*-
import xml.sax
import xml.etree.ElementTree as ET
import re
import pickle
from operator import itemgetter
import os.path
import sys
import codecs


def preprocess_article(string):
    
    string = string.lower()
    string = re.sub(r"/(<![^>]+>)/", '', string)
    string = re.sub(r"/\{\{\s?/", '<', string)
    string = string.replace('}}', ' />')
    string = string.replace('<! />', '')

    
    string = re.sub(r"/'{2,6}/", '', string)
    string = re.sub(r"/[=\s]+External [lL]inks[\s=]+/", '', string)
    string = re.sub(r"/[=\s]+See [aA]lso[\s=]+/", '', string)
    string = re.sub(r"/[=\s]+References[\s=]+/", '', string)
    string = re.sub(r"/[=\s]+Notes[\s=]+/", '', string)
    string = re.sub(r"/\{\{([^\}]+)\}\}/", '', string)
    
    string = re.sub(r"/\[\[([^:\|\]]+)\|([^:\]]+)\]\]/", '$2', string)
    
    string = re.sub(r"/\(\[[^\]]+\]\)/", '', string)
    string = re.sub(r"/\[\[([^:\]]+)\]\]/", '$1', string)
    string = re.sub(r"/\*?\s?\[\[([^\]]+)\]\]/", '', string)
    string = re.sub(r"/\*\s?\[([^\s]+)\s([^\]]+)\]/", '$2', string)
    string = re.sub(r"/\n(\*+\s?)/", '', string)
    string = re.sub(r"/\n{3,}/", '', string)
    string = re.sub(r"/<ref[^>]?>[^>]+>/", '', string)
    string = re.sub(r"/<cite[^>]?>[^>]+>/", '', string)
    
    string = re.sub(r"/={2,}/", '', string)
    string = re.sub(r'/{?class="[^"]+"/', '', string)
    string = re.sub(r'/!?\s?width="[^"]+"/', '', string)
    string = re.sub(r'/!?\s?height="[^"]+"/', '', string)
    string = re.sub(r'/!?\s?style="[^"]+"/', '', string)
    string = re.sub(r'/!?\s?rowspan="[^"]+"/', '', string)
    string = re.sub(r'/!?\s?bgcolor="[^"]+"/', '', string)
    
    string = re.sub(r'/\n\n/', "<br />\n<br />\n", string)
    string = re.sub(r'/\r\n\r\n/', "<br />\r\n<br />\r\n", string)
    
    string = re.sub(r'[^a-z\d\s].*?', '', string) # remove any remaining non-alphanumeric characters
    string = re.sub(r'\n', ' ', string)
    string = re.sub(r'\s+', ' ', string)

    return string



    
def hash_tree(string, article, tree = {}, clean = False):
    words = [[m.group(0), m.start()] for m in re.finditer(r'\S+', string)]
    sorted_words = sorted(words, key=itemgetter(0)) # sort the list to save the hard drive
    
    current_char = ""
    tree = {}
    file = ""
    for word in sorted_words:
        char = word[0][0]
        word[0] = word[0][1:]
        
        if (current_char != char):
            if (current_char != ""):
                file = open('trees/'+current_char+'.tree', 'wb+')
                pickle.dump(tree, file)
                file.close()
            
            current_char = char
            if (os.path.isfile('trees/'+current_char+'.tree') != True):
                file = open('trees/'+current_char+'.tree', 'wb+')
                pickle.dump({}, file)
                file.close()
            
            if (clean): tree = {}
            else :
                file = open('trees/'+char+'.tree', 'rb+')
                tree = pickle.load(file)
                file.close()
        
        add_word_to_tree(tree, word[0], word[1], article)

    file = open('trees/'+char+'.tree', 'wb+')
    pickle.dump(tree, file)
    file.close()

    return tree
    
def add_word_to_tree(tree, word, index, article):
    
    if (len(word) > 0 and (len(tree) < 1 or word[0] not in tree.keys())):
        tree[word[0]] = {} # add first letter of word to tree if not present
    if (len(word) < 1): # terminate recursion
        if ('nodes' not in tree.keys()):
            tree['nodes'] = {article : []}
        if (article not in list(tree['nodes'].keys())):
            tree['nodes'][article] = []
        tree['nodes'][article].append(index) # append word to article
        tree['sorted_nodes'] = sorted(tree['nodes'], key=lambda k: len(tree['nodes'][k]), reverse=True) # sort keys by length of values
    else:
        add_word_to_tree(tree[word[0]], word[1:], index, article) # recursive call, cut first letter and go to appropriate subtree


def add_word_to_dict(word_dict, word, index, article):
    if word not in word_dict.keys():
        word_dict[word] = {article : []}
    if article not in word_dict[word].keys():
        word_dict[word][article] = []
    word_dict[word][article].append(index)

def add_article_to_dict(string, article, clean = False):
    words = [[m.group(0), m.start()] for m in re.finditer(r'\S+', string)]
    sorted_words = sorted(words, key=itemgetter(0)) # sort the list to save the hard drive
    
    folder = 'dicts/'
    current_char = ""
    file = ""
    word_dict = {}
    
    for word in sorted_words:
        index = word[1]
        word = word[0]
        char = word[0]
        
        if (current_char != char):
            if (current_char != ""):
                file = open(folder+current_char, 'wb+')
                pickle.dump(word_dict, file)
                file.close()
            
            current_char = char
            if (os.path.isfile(folder+current_char) != True):
                file = open(folder+current_char, 'wb+')
                pickle.dump({}, file)
                file.close()
            
            if (clean): word_dict = {}
            else :
                file = open(folder+char, 'rb+')
                word_dict = pickle.load(file)
                file.close()
        
        add_word_to_dict(word_dict, word, index, article)

    file = open(folder+char, 'wb+')
    pickle.dump(word_dict, file)
    file.close()
    
    

class WikiContentHandler(xml.sax.ContentHandler):
    
    def __init__(self):
        self.page = False
        self.text = False
        self.title = False
        self.id = False
        self.result = ""
        self.tag = ""
        self.name = ""
    
    def startElement(self, name, attrs):
        if (name == "id"):
            self.id = True
        if (name == "page"): 
            self.page = True
        if (name == "title"):
            self.title = True
        if (name == "text"): 
            self.text = True
        
    def endElement(self, name):
        if(name == "id"):
            self.id = False
        if (name == "page"):
            self.page = False
        if (name == "title"):
            self.title = False
        if (name == "text"):
            self.title = False

            self.result = preprocess_article(self.result)
            file = open('articles/'+self.tag, 'wb+')
            #self.tag = self.tag + "\n"
            #self.name = self.name + "\n"
            self.result = self.tag + "\n" + self.name + "\n" + self.result + "\n"
            #file.write(self.tag.encode("utf-8"))
            #file.write(self.name.encode("utf-8"))
            file.write(self.result.encode("utf-8"))
            file.close()
            print("Parsing " + self.name + " finished")
            
            # Add to tree
            #hash_tree(self.result, self.tag, clean = True)
            
            
            
            # Reset
            self.tag = ""
            self.name = ""
            self.result = ""

    def characters(self, content):
        if (self.id):
            self.tag = content
            #self.result = self.result + content
        if (self.title):
            self.name = content
            #self.result = self.result + content
            #self.result = self.result + "\n--------\n"
        if (self.text):
            self.result = self.result + content
        



