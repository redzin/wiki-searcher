#  -*- coding: utf-8 -*-
import xml.sax
import xml.etree.ElementTree as ET
import re
import pickle
from operator import itemgetter
import os.path
import sys
import codecs


def process_all_articles():
    tree = {}
    for filename in os.listdir('articles'):
        #if filename[:1].lower() == 'ab':
        #    break
        string = preprocess_article(filename)
        hash_tree(string, filename)
        print("Finished processing " + filename)

def preprocess_article(string):
    
    # Get the text part of the article xml by using Python's XML parser
    #tree = ET.parse(filename) # parse the xml tree
    #text = tree.getroot()[1][3][7].text # get the contents of the text-node
    
    #string = ""
    #for c in text:
    #    string += c # convert the list of characters to a Python string
    
    # Clean the string
    string = re.sub(r'\n', ' ', string) # remove new-line
    string = re.sub(r'\{\{.*?\}\}', ' ', string) # remove any {{...}} sections (metadata)
    string = re.sub(r'\<.*?\>', ' ', string) # remove HTML tags
    string = re.sub(r'\[\[([a-zA-Z\d|.:/])*\|', ' ', string) # remove the target of wiki-markup links to other articles
    string = re.sub(r'\=.*?\=', ' ', string) # removes =...=
    string = re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', ' ', string) # remove urls  
    string = string.lower() # lower case everything
    string = re.sub(r'\(.*?\)', ' ', string) # removes parenthses
    #string = re.sub(r'[^a-z\d\s].*?', '', string) # remove any remaining non-alphanumeric characters
    string = re.sub(' +', ' ', string) # remove trailing spaces
    string = re.sub('^ ', '', string) # remove any space at the front of the string

    #file = open(filename, 'wb+')
    #pickle.dump(string, file)
    #file.close()
    
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
        elif (article not in tree['nodes'].keys()):
            tree['nodes'][article] =  []
        tree['nodes'][article].append(index)
    #elif (len(word) == 1): # terminate recursion
    #    if ('nodes' not in tree[word].keys()):
    #        tree[word]['nodes'] = {article : []}
    #    elif (article not in tree[word]['nodes'].keys()):
    #        tree[word]['nodes'][article] =  []
    #    tree[word]['nodes'][article].append(index)
    else:
        add_word_to_tree(tree[word[0]], word[1:], index, article)

def search(s):
    if(os.path.isfile('trees/'+s[0]+'.tree') == True):
        file = open('trees/'+s[0]+'.tree', 'rb+')
        tree = pickle.load(file)
        file.close()
        return search_helper(s[1:], tree)
    else:
        return "Not found"

def search_helper(s, tree):
    if (len(s) < 1):
        print('Invalid search string')
        return {}
    if (len(s) == 1):
        return tree[s]['nodes']
    else:
        return {} if s[0] not in tree.keys() else search_helper(s[1:], tree[s[0]])

class WikiContentHandler(xml.sax.ContentHandler):
    
    def __init__(self):
        self.page = False
        self.text = False
        self.title = False
        self.id = False
        self.result = ""
        self.tag = ""
        self.name = ""
        self.count = 0
    
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
            #pickle.dump(self.tag, file)
            #pickle.dump(self.name, file)
            #pickle.dump(self.result, file)
            file.close()
            print("Parsing " + self.name + " finished")
            self.count = self.count + 1
            self.tag = ""
            self.name = ""
            self.result = ""

            if(self.count > 100):
                exit
        
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
        
        

parser = xml.sax.make_parser()
parser.setContentHandler(WikiContentHandler())
parser.parse(open("enwiki-20170820-pages-articles-multistream.xml","r", encoding="utf8"))

#preprocess_all_articles()

#cat_string = preprocess_article('articles/Cat')
#dog_string = preprocess_article('articles/Dog')
#string_test = 'a cat is not nice'

#tree = {}
#tree = hash_tree(cat_string, 'Cat')
#tree = hash_tree(cat_string, 'Dog')

#path = 'articles/Cat'

#file_read = open(path, 'rb+')
#cat = pickle.load(file_read)
#file_read.close()

#print(search('mammal'))




