
import os
import preprocessing as prep

directory = "articles"

for filename in os.listdir(directory):
    with open(directory+"/"+filename, 'r') as article_file:
        string = article_file.read()
        prep.add_article_to_dict(string, filename)
    
    




