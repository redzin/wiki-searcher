import sys
import pickle
import re

folder = "dicts/"


query = "that[0,5]was[0,5]was"

def search(query):
    
    query = '[0,0]' + query
    query_terms = query.split('[')
    query_terms = [x.split(']') for x in query_terms]
    query_terms.pop(0)
    
    dicts = []
    for q in query_terms:
        file = open(folder+q[1][0], 'rb+')
        word_dict = pickle.load(file)
        if q[1] in word_dict.keys():
            dicts.append(word_dict[q[1]])
        else:
            dicts.append({})
        file.close()

    article_set = dicts[0].keys()
    temp_article_set = []
    for i in range(1,len(query_terms)):
        for key in dicts[i].keys():
            if key in article_set:
                temp_article_set.append(key)
        article_set = temp_article_set 
   
   
    potential_match = {}
    for article in article_set:
        for i in range(0,len(query_terms)):
            if i == 0:
                potential_match[article] = [[x] for x in dicts[i][article]]
            else: 
                for x in potential_match[article]:
                    r = [int(k) for k in query_terms[i][0].split(',')] 
                    for y in dicts[i][article]:
                        if  x[-1] + r[0] - y < 0 and x[-1] + r[1] - y > 0:
                            x.append(y)
                        else:
                            potential_match[article].pop(potential_match[article].index(x))
                            break
    
    matches = {}
    for k, v in potential_match.items():
        if v != []:
            matches[k] = v
        
    print(matches)
    
    #if primary_term in word_dict.keys():
    #    for k, v in word_dict[primary_term]:
    #        file = open('articles/'+k+'.txt', 'w+')
            
            
            
    #        file.write(output)
    #        file.close()
            
    #else:
    #    output = 'No results.'
    
    output = ''
    file = open('output/'+query+'.txt', 'w+')
    file.write(output)
    file.close()
    
    return output


if __name__ == "__main__":
    print(search(query))

