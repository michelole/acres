# Finds synonyms  
# using a n-gram frequency list from the Web
# Stefan Schulz 17 July 2017

import RateAcronymResolutions
from math import *

import Functions
import requests
import html2text
import ling

PROXIES = True

pwd = input("Enter your Kags Proxy pwd")
if PROXIES == True:
    http_proxy = "KA02\SchulzS:" + pwd + "@proxy-static.kages.at:8080"
    https_proxy = http_proxy 
    ftp_proxy = http_proxy
    proxy_dict = {
            "http" : http_proxy,
            "https" : https_proxy,
            "ftp" : ftp_proxy}


NEWLINE = "¶"
NUMERIC = "Ð"
VERBOSE = False
PROBE = True

def ngramsWebDump(url, minNumTokens, maxNumTokens):
# produces an n gram statistics from a Web Query, parsing the first return page
# Stefan Schulz 20170718
# should be used carefully, with delay

    try:
        if PROXIES == True:
            response = requests.get(url, timeout = 1, proxies=proxy_dict)
        else:
            response = requests.get(url, timeout = 1)
    except requests.exceptions.RequestException as e:
        pass
        print("failure")
        return []
    outL = []
    txt = html2text.html2text(response.text)
    txt = txt.replace("**", "").replace("\n", " ").replace("[", "[ ").replace("]", " ]") # .replace("(", "( ").replace(")", " )")
    txt = txt.replace("„", "").replace('"', "").replace("'", "").replace(", ", " , ").replace(". ", " . ")
    out = ""
    #print(txt)
    words = txt.split(" ")
    for word in words:
        if len(word) < 50:
            if not ('\\' in word or '/' in word or '&q=' in word):
                out = out + " " + word
    out = out.replace("  ", "\n").replace("[ ", "\n").replace(" ]", "\n").replace("|", "\n").replace("?", "\n").replace(":", "\n")
    output = ling.WordNgramStat(out, minNumTokens, maxNumTokens)
    for ngram in output:
        outL.append('{:0>4}'.format(output[ngram]) + "\t" + ngram)
    outL.sort(reverse=True)     
    return outL

if PROBE == True:
    acro="AV"
    q="AV Blocks"
    # PROBE    
    import pickle
    m = pickle.load(open("pickle//morphemes.p", "rb")) 
    #p = ngramsWebDump("https://www.google.at/search?q=EKG+Herz", 1, 10)
    #p = ngramsWebDump("http://www.bing.de/search?cc=de&q=ekg+Herz", 1, 10)
    p = ngramsWebDump('http://www.bing.de/search?cc=de&q="' + q + '"', 1, 10)
    #p = ngramsWebDump('http://www.bing.de/search?cc=de&q=' + q , 1, 10)
    #f = open("c:\\Users\\schulz\\Nextcloud\\Terminology\\Corpora\\staging\\out.txt", 'wt')
    #f.write("\n".join(p))
    #f.close()
    #print(p)

    for line in p:
        full = line.split("\t")[1]
        cnt = line.split("\t")[0]
        s = RateAcronymResolutions.GetAcronymScore(acro, full, m)
        if s > 0.01:
            print(str(s * int(cnt)) + "\t" +  line)
    
    







 
