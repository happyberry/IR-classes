# Author: Michal Tomczyk
# michal.tomczyk@cs.put.poznan.pl
# Poznan University of Technology
# Institute of Computing Science
# Laboratory of Intelligent Decision Support Systems
#-------------------------------------------------------------------------
import urllib.request as req
import sys
import os
import numpy

from html.parser import HTMLParser

###################################
class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.outputlist = []
    def handle_starttag (self, tag , attrs):
        if tag == 'a':
            self.outputlist.append (dict(attrs).get('href'))
###################################

      
#-------------------------------------------------------------------------
### generatePolicy classes
  
  
# Dummy fetch policy. Returns first element. Does nothing ;)
class Dummy_Policy:
    def getURL(self, c, iteration):
        if len(c.URLs) == 0:
            return None
        else:
            return c.seedURLs[0]
            
    def updateURLs(self, c, retrievedURLs, retrievedURLsWD, iteration):
        pass

# LIFO_Policy fetch policy. Does something ;)
class LIFO_Policy:
    def __init__(self, c):
        self.lifo_urls = c.seedURLs 
        
    def getURL(self, c, iteration):
        if len(self.lifo_urls) == 0:
            self.lifo_urls = c.seedURLs
        tmp = self.lifo_urls[-1]
        self.lifo_urls = self.lifo_urls[:-1]
        return tmp
            
    def updateURLs(self, c, retrievedURLs, retrievedURLsWD, iteration):
        tmpList = list(retrievedURLs)
        tmpList.sort(key=lambda url: url[len(url) - url[::-1].index('/'):])
        for element in tmpList:
            self.lifo_urls.append(element)

# LIFO_Cycle_Policy fetch policy. Does something ;)
class LIFO_Cycle_Policy:
    def __init__(self, c):
        self.lifo_urls = c.seedURLs
        self.fetched = set()
        
    def getURL(self, c, iteration):
        
        while len(self.lifo_urls) != 0 and self.lifo_urls[-1] in self.fetched:
            self.lifo_urls = self.lifo_urls[:-1]

        if len(self.lifo_urls) == 0:
            self.lifo_urls = c.seedURLs
            self.fetched = set()

        tmp = self.lifo_urls[-1]
        self.lifo_urls = self.lifo_urls[:-1]
        self.fetched.add(tmp)
        return tmp
            
    def updateURLs(self, c, retrievedURLs, retrievedURLsWD, iteration):
        tmpList = list(retrievedURLs)
        tmpList.sort(key=lambda url: url[len(url) - url[::-1].index('/'):])
        for element in tmpList:
            self.lifo_urls.append(element)
        
# LIFO_Authority_Policy fetch policy. Does something ;)
class LIFO_Authority_Policy:
    def __init__(self, c):
        self.lifo_urls = c.seedURLs
        self.fetched = set()
        self.authority_level = {}
        self.list_of_probability = None
        self.all_authority = 0
        self.cleared = False

    #uzupelnia prawdopodobienstwa wyboru na podstawie sumy 'authority'
    def updateListOfProbability (self):
        self.list_of_probability = []
        self.all_authority = sum(self.authority_level.values())
        if self.all_authority != 0:
            for url in self.authority_level:
                self.list_of_probability.append(self.authority_level[url]/self.all_authority)

    def getURL(self, c, iteration):
        if self.cleared: #wybieranie z prawdopodobienstwa
            selected = numpy.random.choice(list(self.authority_level.keys()), p = self.list_of_probability)
            return selected

        else: #funkcja przed wyczyszczeniem listy i uzupelnieniem prawdopodobienstwa
            while len(self.lifo_urls) != 0 and self.lifo_urls[-1] in self.fetched:
                self.lifo_urls = self.lifo_urls[:-1]

            if len(self.lifo_urls) == 0:
                self.lifo_urls = c.seedURLs
                self.fetched = set()

                for url in c.URLs: #bez tego nie lapie linkow do ktorych nic nie wchodzi, tak zapisuje wszystkim 1, a jesli jest w incoming to nastepnym forem zaktualizuje
                    self.authority_level[url] = 1
                for incomingURL in c.incomingURLs:
                    self.authority_level[incomingURL] = len(c.incomingURLs[incomingURL]) + 1
                self.updateListOfProbability() #uaktualnia liste prawdopodobienstw
                self.cleared = True
            tmp = self.lifo_urls[-1]
            self.lifo_urls = self.lifo_urls[:-1]
            self.fetched.add(tmp)
            return tmp
            
    def updateURLs(self, c, retrievedURLs, retrievedURLsWD, iteration):
        tmpList = list(retrievedURLs)
        tmpList.sort(key=lambda url: url[len(url) - url[::-1].index('/'):])
        for element in tmpList:
            self.lifo_urls.append(element)
        
# FIFO_Policy fetch policy. Does something ;)
class FIFO_Policy:
    def __init__(self, c):
        self.fifo_urls = c.seedURLs 
        
    def getURL(self, c, iteration):
        if len(self.fifo_urls) == 0:
            self.fifo_urls = c.seedURLs
        tmp = self.fifo_urls[0]
        self.fifo_urls = self.fifo_urls[1:]
        return tmp
            
    def updateURLs(self, c, retrievedURLs, retrievedURLsWD, iteration):
        tmpList = list(retrievedURLs)
        tmpList.sort(key=lambda url: url[len(url) - url[::-1].index('/'):])
        for element in tmpList:
            self.fifo_urls.append(element)
        

#-------------------------------------------------------------------------
# Data container
class Container:
    def __init__(self):
        # The name of the crawler"
        self.crawlerName = "IRbot"
        # Example ID
        self.example = "exercise3"
        # Root (host) page
        self.rootPage = "http://www.cs.put.poznan.pl/mtomczyk/ir/lab1/" + self.example
        # Initial links to visit
        self.seedURLs = ["http://www.cs.put.poznan.pl/mtomczyk/ir/lab1/"
            + self.example + "/s0.html"]
        # Maintained URLs
        self.URLs = set([])
        # Outgoing URLs (from -> list of outgoing links)
        self.outgoingURLs = {}
        # Incoming URLs (to <- from; set of incoming links)
        self.incomingURLs = {}
        # Class which maintains a queue of urls to visit. 
        self.generatePolicy = LIFO_Authority_Policy(self)
        # Page (URL) to be fetched next
        self.toFetch = None
        # Number of iterations of a crawler. 
        self.iterations = 50

        # If true: store all crawled html pages in the provided directory.
        self.storePages = True
        self.storedPagesPath = "./" + self.example + "/pages/"
        # If true: store all discovered URLs (string) in the provided directory
        self.storeURLs = True
        self.storedURLsPath = "/" + self.example +"/urls/"
        # If true: store all discovered links (dictionary of sets: from->set to),
        # for web topology analysis, in the provided directory
        self.storeOutgoingURLs = True
        self.storedOutgoingURLs = "/" + self.example + "/outgoing/"
        # Analogously to outgoing
        self.storeIncomingURLs = True
        self.storedIncomingURLs = "/" + self.example + "/incoming/"
        
        
        # If True: debug
        self.debug = False 
        
def main():

    # Initialise data
    c = Container()
    # Inject: parse seed links into the base of maintained URLs
    inject(c)
    
    # Iterate...
    for iteration in range(c.iterations):
    
        if c.debug: 
            print("=====================================================")
            print("Iteration = " + str(iteration + 1) )
            print("=====================================================")
        # Prepare a next page to be fetched
        generate(c, iteration)
        if (c.toFetch == None):
            if c.debug:
                print("   No page to fetch!")
            continue
                
        # Generate: it downloads html page under "toFetch URL"
        page = fetch(c)
    
        if page == None:
            if c.debug:
                print("Unexpected error; skipping this page")
            removeWrongURL(c)
            continue
            
        # Parse file
        htmlData, retrievedURLs = parse(c, page, iteration)
        
        # Store pages
        if c.storePages:
            storePage(c, htmlData)
        
        ### normalise retrievedURLs
        retrievedURLs = getNormalisedURLs(retrievedURLs)
        
        ### update outgoing/incoming links
        updateOutgoingURLs(c, retrievedURLs)
        updateIncomingURLs(c, retrievedURLs)
        
        ### Filter out some URLs
        retrievedURLs = getFilteredURLs(c, retrievedURLs)
        
        ### removeDuplicates
        retrievedURLsWD = removeDuplicates(c, retrievedURLs)
        
        ### update urls
        c.generatePolicy.updateURLs(c, retrievedURLs, retrievedURLsWD, iteration)
        
        # Add newly obtained URLs to the container   
        if c.debug:
            print("   Maintained URLs...")
            for url in c.URLs:
                print("      " + str(url))
        
        if c.debug:
            print("   Newly obtained URLs (duplicates with maintaines URLs possible) ...")
            for url in retrievedURLs:
                    print("      " + str(url))
        if c.debug:
            print("   Newly obtained URLs (without duplicates) ...")
            for url in retrievedURLsWD:
                    print("      " + str(url))        
            for url in retrievedURLsWD:
                c.URLs.add(url)

    # store urls
    if c.storeURLs:
        storeURLs(c)
    if c.storeOutgoingURLs:
        storeOutgoingURLs(c)
    if c.storeIncomingURLs:
        storeIncomingURLs(c)            
    

#-------------------------------------------------------------------------
# Inject seed URL into a queue (DONE)
def inject(c):
    for l in c.seedURLs:
        if c.debug: 
            print("Injecting " + str(l))
        c.URLs.add(l)

#-------------------------------------------------------------------------
# Produce next URL to be fetched (DONE)
def generate(c, iteration):
    url = c.generatePolicy.getURL(c, iteration)
    if url == None:
        if c.debug:
            print("   Fetch: error")
        c.toFetch = None
        return None
    # WITH NO DEBUG!
    print("   Next page to be fetched = " + str(url)) 
    c.toFetch = url
    

#-------------------------------------------------------------------------
# Generate (download html) page (DONE)
def fetch(c):
    URL = c.toFetch
    if c.debug: 
        print("   Downloading " + str(URL))
    try:
        opener = req.build_opener()
        opener.addheadders = [('User-Agent', c.crawlerName)]
        webPage = opener.open(URL)
        return webPage
    except:
        return None 
        
#-------------------------------------------------------------------------  
# Remove wrong URL (TODO)
def removeWrongURL(c):
    c.URLs.remove(c.toFetch)
    #TODO
    pass
    
#-------------------------------------------------------------------------  
# Parse this page and retrieve text (whole page) and URLs (TODO)
def parse(c, page, iteration):
    # data to be saved (DONE)
    htmlData = page.read()
    # obtained URLs (TODO)
    p = Parser ()
    p.feed (str(htmlData))
    p.outputlist # list of URLs
#    retrievedURLs = set([])
    retrievedURLs = set(p.outputlist)
    if c.debug:
        print("Extracted " + str(len(retrievedURLs)) + " links")

    return htmlData, retrievedURLs

#-------------------------------------------------------------------------  
# Normalise newly obtained links (TODO)
def getNormalisedURLs(retrievedURLs):
    retrievedURLs = set([url.lower() for url in retrievedURLs])
    return retrievedURLs
    
#-------------------------------------------------------------------------  
# Remove duplicates (duplicates) (TODO)
def removeDuplicates(c, retrievedURLs):
    retrievedURLs = retrievedURLs.difference(c.URLs)
    return retrievedURLs

#-------------------------------------------------------------------------  
# Filter out some URLs (TODO)
def getFilteredURLs(c, retrievedURLs):
    toLeft = set([url for url in retrievedURLs if url.lower().startswith(c.rootPage)])
    if c.toFetch in toLeft:
        toLeft.remove(c.toFetch)
    if c.debug:
        print("Filtered out " + str(len(retrievedURLs) - len(toLeft)) + " urls")  
    return toLeft
    
#-------------------------------------------------------------------------  
# Store HTML pages (DONE)  
def storePage(c, htmlData):
    
    relBeginIndex = len(c.rootPage)
    totalPath = "./" + c.example + "/pages/" + c.toFetch[relBeginIndex + 1:]
    
    if c.debug:
        print("   Saving HTML page " + totalPath + "...")
    
    totalDir = os.path.dirname(totalPath)
    
    if not os.path.exists(totalDir):
        os.makedirs(totalDir)
        
    with open(totalPath, "wb+") as f:
        f.write(htmlData)
        f.close()
        
#-------------------------------------------------------------------------  
# Store URLs (DONE)  
def storeURLs(c):
    relBeginIndex = len(c.rootPage)
    totalPath = "./" + c.example + "/urls/urls.txt"
    
    if c.debug:
        print("Saving URLs " + totalPath + "...")
    
    totalDir = os.path.dirname(totalPath)
    
    if not os.path.exists(totalDir):
        os.makedirs(totalDir)
        
    data = [url for url in c.URLs]
    data.sort()
        
    with open(totalPath, "w+") as f:
        for line in data:
            f.write(line + "\n")
        f.close()
        
   
#-------------------------------------------------------------------------  
# Update outgoing links (DONE)  
def updateOutgoingURLs(c, retrievedURLsWD):
    if c.toFetch not in c.outgoingURLs:
        c.outgoingURLs[c.toFetch] = set([])
    for url in retrievedURLsWD:
        c.outgoingURLs[c.toFetch].add(url)
        
#-------------------------------------------------------------------------  
# Update incoming links (DONE)  
def updateIncomingURLs(c, retrievedURLsWD):
    for url in retrievedURLsWD:
        if url not in c.incomingURLs:
            c.incomingURLs[url] = set([])
        c.incomingURLs[url].add(c.toFetch)
    
#-------------------------------------------------------------------------  
# Store outgoing URLs (DONE)  
def storeOutgoingURLs(c):
    relBeginIndex = len(c.rootPage)
    totalPath = "./" + c.example + "/outgoing_urls/outgoing_urls.txt"
    
    if c.debug:
        print("Saving URLs " + totalPath + "...")
    
    totalDir = os.path.dirname(totalPath)
    
    if not os.path.exists(totalDir):
        os.makedirs(totalDir)
        
    data = [url for url in c.outgoingURLs]
    data.sort()
        
    with open(totalPath, "w+") as f:
        for line in data:
            s = list(c.outgoingURLs[line])
            s.sort()
            for l in s:
                f.write(line + " " + l + "\n")
        f.close()
        

#-------------------------------------------------------------------------  
# Store incoming URLs (DONE)  
def storeIncomingURLs(c):
    relBeginIndex = len(c.rootPage)
    totalPath = "./" + c.example + "/incoming_urls/incoming_urls.txt"
    
    if c.debug:
        print("Saving URLs " + totalPath + "...")
    
    totalDir = os.path.dirname(totalPath)
    
    if not os.path.exists(totalDir):
        os.makedirs(totalDir)
        
    data = [url for url in c.incomingURLs]
    data.sort()
        
    with open(totalPath, "w+") as f:
        for line in data:
            s = list(c.incomingURLs[line])
            s.sort()
            for l in s:
                f.write(line + " " + l + "\n")
        f.close()
        


if __name__ == "__main__":
    main()
