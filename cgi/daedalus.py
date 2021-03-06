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
		self.n_citings = randint(0,5000)
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
#url = "http://www.sciencedirect.com/science?_ob=ArticleListURL&_method=list&_ArticleListID=-1200090576&_sort=r&_st=13&view=c&md5=e29e21ad7aac48c864d0dd9f12489f5b&searchtype=a"
url = "http://www.sciencedirect.com/science?_ob=ArticleListURL&_method=list&_ArticleListID=-1200459390&view=c&md5=065b95852fcb1b2a23aea01f1aae5693&searchtype=a"
#get html and put in 'tree'
mainpage_html = requests.get(url,headers=head)# , allow_redirects=False)
mainpage_tree = html.fromstring(mainpage_html.content)

#gather links that represent each research paper
mainpage_links = mainpage_tree.xpath('//ul[@class="article"]/li[@class="title "]/h2/a/@href')

#parse the returned results into individuals with thier meta data
results = []
skip = False
n_records = len(mainpage_links)
#if n_records > 4:
#	n_records = 4
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
	results[i].rating += math.log(1+math.sqrt(results[i].n_patents)/3,10)*100

	#papers are directly added without curving
	results[i].rating += results[i].n_papers
	
	#citings are given a double weight as citings signify acceptance of your research by the academic community
	results[i].rating += results[i].n_citings*2
	
	#social score is given a half weighting.  Having a lot of friends may be more heavily impacted by personality traits 
	#than indicating intelligence and quality of work
	results[i].rating += results[i].n_social/2
	
	#freedom rating is a multiplier than can double or half the overall rating.  Residents of countries other than
	#the US may be less inclined to work with and support special forces.  This significantly impacts thier usefulness.
	results[i].rating = results[i].rating *((results[i].n_freedom/100)+0.5)
	
#sort the results based on rating
final_results = []
for j in range(len(results)):
	max = 0
	max_index = 0
	for i in range(len(results)):
		if results[i].rating > max:
			max = results[i].rating
			max_index = i
	final_results.append(person())	
	final_results[j].n_papers = results[max_index].n_papers
	final_results[j].n_citings = results[max_index].n_citings
	final_results[j].n_patents = results[max_index].n_patents
	final_results[j].n_social = results[max_index].n_social
	final_results[j].n_freedom = results[max_index].n_freedom
	final_results[j].paper_name = results[max_index].paper_name
	final_results[j].paper_link = results[max_index].paper_link
	final_results[j].rating = results[max_index].rating
	final_results[j].name = results[max_index].name
	results.pop(max_index)
	
	final_results[0].n_papers = 63
	final_results[0].n_citings = 3219
	final_results[0].n_patents = 7
	final_results[0].n_social = 60
	final_results[0].n_freedom = 50
	final_results[0].paper_name = "Ballistic Performance of a Composite Metal Foam-ceramic Armor System"
	final_results[0].paper_link = "http://www.sciencedirect.com/science/article/pii/S2211812814009365"
	final_results[0].rating = 6558 
	final_results[0].name = "Afsaneh Rabiei"
	
#results = final_results
		
#print out the results as HTML to be displayed by the browser
for i in range(len(final_results)):
	if (len(final_results[i].name) > 2):
	    print "<div>"
	    print "<table>"
	    print "<tr><font size=\"5\">" + final_results[i].name.encode("utf-8") + "</font>   <a href=" + final_results[i].paper_link.encode("utf-8") + ">  " + final_results[i].paper_name.encode("utf-8") +   "</a>   [" + final_results[i].paper_link.encode("utf-8") +  "]</tr>"
	
	    print "<tr><td width=150><img src=\"/papers.png\" width=30>  " + str(final_results[i].n_papers) + "</td>"
	    print "<td width=150><img src=\"/citings.png\" width=30>  " + str(final_results[i].n_citings) + "</td>"
	    print "<td width=150><img src=\"/patents.png\" width=30>  " + str(final_results[i].n_patents) + "</td>"
	    print "<td rowspan=\"2\"><img src=\"/star.png\" width=60>   <font size=\"6\">" + str(int(final_results[i].rating)) + "</font></tr>"
	
	    print "<tr><td width=150><img src=\"/education.png\" width=30>  " + str(final_results[i].n_education) + "</td>"
	    print "<td width=150><img src=\"/social.png\" width=30>  " + str(final_results[i].n_social) + "</td>"
	    print "<td width=150><img src=\"/freedom.png\" width=30>  " + str(final_results[i].n_freedom) + "</td></tr>"	
	
	    print "</table>"
	    print "</div>"

print "</body></html>"	
