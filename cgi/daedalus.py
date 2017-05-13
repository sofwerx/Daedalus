import sys
sys.stderr = sys.stdout
import os
from cgi import escape
from lxml import html
from time import sleep
from random import randint
import requests
import random
import math

#create a data structure for the individuals that we find
class person:
    def __init__(self, n_papers=0, n_citings=0, n_patents=0, n_education=0, n_social=0, n_freedom=0):
		self.name = ""
		self.n_papers = randint(0,1000)
		self.n_citings = randint(0,1000)
		self.n_patents = randint(0,20)
		self.n_education = "School"
		self.n_social = randint(0,100)
		self.n_freedom = randint(0,100)
		self.paper_name = ""
		self.paper_link = ""
		self.rating = 0

#all "print" outputs from this script are the HTML that gets rendered for the webpage
print "Content-type: text/html"
print
print "<html><head><style>"
print ".loader {"
print "   position: fixed;"
print "   left: 0px;"
print "   top: 0px;"
print "   width: 100%;"
print "   height: 100%;"
print "   z-index: 9999;"
print "   background: url('/DaedalusLoading.gif') 50% 50% no-repeat rgb(249,249,249);}"
print "</style><title>Situation snapshot</title>"
print "<script src=\"//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js\"></script> "
print "<script type=\"text/javascript\">"
print "$(window).load(function() { "
print "$(\".loader\").fadeOut(\"slow\");" 
print "}) "
print "</script>"
print "</head>"
print "<body>"
print "<div class=\"loader\"></div>"
print "<center><table><tr>"
print "<div><center><img style=\"padding-top:15px\" height=\"200\" src=\"/logo2.jpg\" ></center></div>"
print "</tr></table></center>"


#user agent for my browser
#check: http://www.whoishostingthis.com/tools/user-agent/
head = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0"}

#html for a science direct page AFTER entering in search query
url = "http://www.sciencedirect.com/science?_ob=ArticleListURL&_method=list&_ArticleListID=-1200090576&_sort=r&_st=13&view=c&md5=e29e21ad7aac48c864d0dd9f12489f5b&searchtype=a"

#get html and put in 'tree'
mainpage_html = requests.get(url,headers=head)# , allow_redirects=False)
mainpage_tree = html.fromstring(mainpage_html.content)

#gather links that represent each research paper
mainpage_links = mainpage_tree.xpath('//ul[@class="article"]/li[@class="title "]/h2/a/@href')

#parse the returned results into individuals with thier meta data
results = []
skip = False
n_records = len(mainpage_links)
if n_records > 4:
	n_records = 4
for i in range(0,n_records):

    skip = False
    #picks a specific url from the main page. this url represents an research paper that we will
    # "click" on
    newurl = mainpage_links[i]

    #grab the html of this new page, and store it in the tree
    try:
        r = requests.get(newurl,headers=head)#, allow_redirects=False)
    except:
        skip = True
		
    if(skip==False):
        rtree = html.fromstring(r.content)

        #gather the name of the paper
        nameofpaper = rtree.xpath('//div[@id="frag_1"]/h1/text()')

        #gather who published the paper  
        namesofpeople = rtree.xpath('//ul[@class="authorGroup noCollab svAuthor"]/li/a/text()')
        for j in range(len(namesofpeople)):
            results.append(person())
            results[i].name = namesofpeople[j]
            results[i].paper_name = nameofpaper[0]
            results[i].paper_link = newurl
        #gather the abstract
        abstract = rtree.xpath('//div[@class="abstract svAbstract "]/p/text()')

#rating algorithm
for i in range(len(results)):
	#algorithm
	#based on how impressive certain stats are
	
	#patents are logarthmic curve that give a higher percentage of credability for your first few than your 1000th
	results[i].rating += math.log(1+math.sqrt(results[i].n_patents)/3,10)
	#print "i = " + str(i)
	#print "rating: " + str(results[i].rating)
	#print "patents: " + str(results[i].n_patents)
	#papers are directly added without curving
	results[i].rating += results[i].n_papers
	#print "rating: " + str(results[i].rating)
	#print "papers: " + str(results[i].n_papers)
	
	#citings are given a double weight as citings signify acceptance of your research by the academic community
	results[i].rating += results[i].n_citings*2
	#print "rating: " + str(results[i].rating)
	#print "citings: " + str(results[i].n_citings)
	
	#social score is given a half weighting.  Having a lot of friends may be more heavily impacted by personality traits 
	#than indicating intelligence and quality of work
	results[i].rating += results[i].n_social/2
	#print "rating: " + str(results[i].rating)
	#print "social: " + str(results[i].n_social)
	
	#freedom rating is a multiplier than can double or half the overall rating.  Residents of countries other than
	#the US may be less inclined to work with and support special forces.  This significantly impacts thier usefulness.
	results[i].rating = results[i].rating *((results[i].n_freedom/100)+0.5)
	#print "rating: " + str(results[i].rating)
	#print "freedom: " + str(results[i].n_freedom)
	
#sort the results based on rating

		
#print out the results as HTML to be displayed by the browser
for i in range(len(results)):
	if (len(results[i].name) > 2):
	    print "<div>"
	    print "<table>"
	    print "<tr><font size=\"5\">" + results[i].name.encode("utf-8") + "</font>   <a href=" + results[i].paper_link.encode("utf-8") + ">  " + results[i].paper_name.encode("utf-8") +   "</a>   [" + results[i].paper_link.encode("utf-8") +  "]</tr>"
	
	    print "<tr><td width=150><img src=\"/papers.png\" width=30>  " + str(results[i].n_papers) + "</td>"
	    print "<td width=150><img src=\"/citings.png\" width=30>  " + str(results[i].n_citings) + "</td>"
	    print "<td width=150><img src=\"/patents.png\" width=30>  " + str(results[i].n_patents) + "</td>"
	    print "<td rowspan=\"2\"><img src=\"/star.png\" width=60>   <font size=\"6\">" + str(int(results[i].rating)) + "</font></tr>"
	
	    print "<tr><td width=150><img src=\"/education.png\" width=30>  " + str(results[i].n_education) + "</td>"
	    print "<td width=150><img src=\"/social.png\" width=30>  " + str(results[i].n_social) + "</td>"
	    print "<td width=150><img src=\"/freedom.png\" width=30>  " + str(results[i].n_freedom) + "</td></tr>"	
	
	    print "</table>"
	    print "</div>"

print "</body></html>"	
