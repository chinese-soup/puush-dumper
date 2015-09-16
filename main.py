#!/usr/bin/env python2
# coding=utf-8
# Made and tested on Python 2.7.8
# Tested on CYGWIN_NT-6.1 unko 1.7.33-2(0.280/5/3) 2014-11-13 15:47 x86_64 Cygwin
# Usage: ./main.py --help
# TODO: cleanup, methods, classes

import os, sys, json, argparse, re

reload(sys) # pygay2 shit
sys.setdefaultencoding("utf-8")

try:
	import requests
except: 
	print "The \"requests\" library is missing. Please install it and try again."
	sys.exit(1)

try:
	from BeautifulSoup import BeautifulSoup
except: 
	print "The \"BeautifulSoup\" library is missing. Please install it and try again."
	sys.exit(1)

class ConfigParser(object):
	"""ConfigParser class"""
	def __init__(self, args):		
		self.config_filename = "config.json" 
		if args.config:
			self.config_filename = args.config
		try:
			self.config_data = json.load(open(self.config_filename))
		except Exception as ex:					
			print "Config file could not be loaded. Please check if the path to the config file is correct and the file itself is a valid JSON.\nSee config.json.example for an example of a working config file."

	def config_parse(self):
		self.login_info = {"email": "", "password": "", "login": "Login+%E2%86%92"}

		if self.config_data is not []:
			self.login_info["email"] = self.config_data["email"]
			self.login_info["password"] = self.config_data["password"]
		else: 
			print "Config file could not be read properly. Please check if the path to the config file is correct and the file itself is fine.\nSee config.json.example for an example of a working config file."
			sys.exit(1)
		return self.login_info
		

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Dump all your files from your puush account.")
	parser.add_argument("-c", "--config", help="Alternative path to the config file. Default is ./config.json")
	parser.add_argument("-n", "--no-download", help="Don't download the files, just dump the links to stdout.", action="store_true")
	parser.add_argument("-p", "--pool", help="Change the pool (aka the puush folder) to dump. Optional, as it defaults to your selected default one on puush.me.")
	parser.add_argument("-l", "--list-pools", help="Dump the list of your pools. (aka the puush folder, e.g. Private/Public/Gallery/Custom/...)", action="store_true")

	args = parser.parse_args()

	cp = ConfigParser(args)
	login_info = cp.config_parse()
	
	session_s = requests.Session()
	
	response_s = session_s.post("http://puush.me/login/go", data=login_info, allow_redirects=False) # don't redirect, we are gonna do another request ourselves, anyway
	if(response_s.status_code != 302):
		print "Error while logging in. Check your credentials."
		sys.exit(1)
	
	base_url = "http://puush.me/account?list"

	main_page = session_s.get(base_url)
	main_page_text = main_page.text
	soup = BeautifulSoup(main_page_text)
	
	# Pool list #
	if(args.list_pools == True):
		print "Based on the arguments given, you chose to list pools only."

		puush_pools_div = soup.findAll("div",attrs={"id":"puush_pools"}) # this should always return just one, so fuck for
		puush_pools_links = puush_pools_div[0].findAll("a")
		
		pools = {}
		for i in puush_pools_links:
			title = i["title"]
			href = re.sub(r"\/account\/\?pool=([0-9]+)", r"\1", i["href"]) # /account/?pool=number ==> number
			pools[title] = href
		
		print "Listing pools:"

		for name, href in pools.iteritems():
			print "ID: {0} | Name: {1}".format(href, name)

		print "\nTo choose a pool to dump use the \"--pool <ID>\" argument."
		print "Exiting."
		sys.exit(0)

	paramss = {"page": 1}
	
	while(True):
		page = session_s.get(base_url, params=paramss)
		page_text = page.text
		soup = BeautifulSoup(page_text)
		
		file_links = soup.findAll("a", attrs={"onclick": re.compile("puush_hist_select.*")})
		for link in file_links:
			print link["href"]

		next_page = soup.find("a", text="&raquo;", attrs={ "class": "noborder"}) # inside of the <a> tag for “next page”
		
		if(next_page is not None):
			next_page_a = next_page.parent # the next page <a> tag
			next_page_number = re.sub(r"\?page=([0-9]+)", r"\1", next_page_a["href"])
			paramss["page"] = next_page_number

		else:
			print "No next page link found, we've reached the end. Probably. Who knows. This code's p bad."
			break

	if(args.no_download == True):
		pass
