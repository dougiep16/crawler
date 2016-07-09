#!/usr/bin/env python
#python crawler.py https://www.countysportszone.com?d=39

import logging
import requests
import sys
from bs4 import BeautifulSoup
from urlparse import urlparse

logging.basicConfig()
logger = logging.getLogger('crawler')
logger.setLevel(logging.DEBUG)

ROOT_URL = "https://www.countysportszone.com"

#go this deep
MAX_DEPTH = 10

# keep track of what urls weve crawled so we dont crawl them again
URLS_CRAWLED = {} #use dict for faster look ups

#BeautifulSoup parser
BS_PARSER = "html5lib"

def checkRootUrl(link):
	'''
	Make sure the root url is our site
	'''
	parsed_uri = urlparse( link )
	domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

	return domain == ROOT_URL


def isLinkValid(link):
	'''
	determine if the link is valid

	link - the url found in the link
	'''

	link = link.strip()

	if not link:
		#this is nothing
		return False

	if link[0] == "#":
		#logger.debug("{} Invalid. This is an anchor".format(link))
		return False

	if link in URLS_CRAWLED:
		#logger.debug("{} Invalid. Already crawled it.".format(link))
		return False

	if not checkRootUrl(link):
		#logger.debug("{} Invalid. Root url is not ours".format(link))
		return False


	return True

def linkTransformer(link):
	'''
	if you need to modify the link
	'''

	#prepend with the https:
	if link.startswith("//"):
		link = "https:" + link

	#prepend the root url
	elif link.startswith("/"):
		link = ROOT_URL + link


	return link

def addUrl(url):
	'''
	Track the urls we've crawled

	url - the url of the page about to be crawled
	'''

	global URLS_CRAWLED

	URLS_CRAWLED[url] = True

	logger.info("Crawl Counter: {}".format(len(URLS_CRAWLED)))

	return 

def crawlPage(url, depth=0):
	'''
	does the actual retreival of the html, and finds links.

	url - the full url to be crawled
	depth - how deep we are from the first page we crawled
	'''
	if depth >= MAX_DEPTH:
		logger.info("MAx depth reached")
		return

	#keep track of the url, so we dont crawl it again
	addUrl(url)

	logger.info("{} Crawling: {}".format(depth, url))

	#make the GET request
	response = requests.get(url)

	#parse the response content
	logger.info("Response Code: {}, from {}".format(response.status_code, url))
	soup = BeautifulSoup(response.content, BS_PARSER)

	#get all the links
	links = soup.find_all('a', href=True)
	logger.info("Found {} links on {}".format(len(links), url))


	for link in links:
		#all we want is the href
		link = link['href']

		logger.debug("Found link: {}".format(link))

		#fix the link
		link = linkTransformer(link)

		logger.debug("Transformed to: {}".format(link))

		#make sure the link is valid (whatever the hell valid is for your use case)
		if isLinkValid(link):

			#now that the link is valid, lets crawl that page
			#we will increment the depth
			crawlPage(link, depth+1)

	return 

if __name__ == '__main__':
	url = sys.argv[1]
	logger.info("Starting with url: {}".format(url))

	#start the crawling
	crawlPage(url)

	logger.info("Done")