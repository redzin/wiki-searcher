import sys
import pickle

folder = "dicts/"


query = "that[0,20]cat"

def search(query):
    
    query_terms = query.split('[')    
    
    file = open(folder+query[0], 'rb+')
    word_dict = pickle.load(file)
    file.close()

    return query_terms


if __name__ == "__main__":
    print(search(query))

