#!/usr/bin/env python2
# coding=utf-8
# Made and tested on Python 2.7.8
# Tested on CYGWIN_NT-6.1 unko 1.7.33-2(0.280/5/3) 2014-11-13 15:47 x86_64 Cygwin
# Usage: ./main.py --help
# TODO: cleanup, methods, classes

import os, sys, json, argparse, re, codecs

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

class PuushDumper(object):
	"""PuushDumper"""
	def __init__(self):
		args = Arguments(description="Dump all your files from your puush account.").parse()
		cp = ConfigParser(args)
		login_info = cp.config_parse()

		self.session_s = requests.Session()
		self.login(login_info)
		self.base_url = "http://puush.me/account?list"
		self.filename = args.text_output or "puush.txt"
		self.all_links = []

		if args.list_pools: 
			self.list_pools()

		paramss = {"page": 1, "pool": args.pool} if(args.pool is not None) else {"page": 1}		
		print "PARAMSS: ", paramss
	
		while(True):
			print "Start loading page #{0}".format(paramss["page"])
			page = self.session_s.get(self.base_url, params=paramss)
			page_text = page.text
			soup = BeautifulSoup(page_text)
			
			file_links = soup.findAll("a", attrs={"onclick": re.compile("puush_hist_select.*")}) # find all the file links on the page
			for link in file_links:
				self.all_links.append(link["href"])

			next_page_btn = soup.find("a", text="&raquo;", attrs={ "class": "noborder"}) # inside of the <a> tag for “next page”
			
			if next_page_btn is not None:
				next_page_a = next_page_btn.parent # the next page <a> tag
				next_page_number = re.sub(r"\?page=([0-9]+)", r"\1", next_page_a["href"])
				print "End of loading page #{0}".format(paramss["page"])
				paramss["page"] = next_page_number

			else:
				print "No next page link found, we've probably reached the end. This code's p bad, so who knows if we actually did."
				print "End of scraping.\n----------------"
				break

		# done #

		if args.no_download:
			if args.text_output:
				#if os.path.exists(os.path.join(os.path.dirname(__file__), self.filename)):
				#	print "The selected filename '{0}' already exists. Are you sure you want to overwrite it? [Y/n]: "
				#	choice = raw_input() or "y"

				#if choice.lower() != "n":

				try:
					print "Starting text output."
					self.dump_links()
					print "Done. {0} lines sucessfully written into '{1}'.".format(len(self.all_links), self.filename)
				except Exception as exp:
					print "Shit happened: {0}".format(exp)
			else:
				print "---------------- Start: 	Cut here ----------------"
				for link in self.all_links:
					print link
				print "---------------- End: 	Cut here ----------------"
		else:
			print "Starting downloader."
			downloader = Downloader(self.all_links)

		print "Exiting."

	def dump_links(self):
		print "Opening file '{0}' for writing.".format(self.filename)
	
		filestream = codecs.open(self.filename, "w", "utf-8")
		for link in self.all_links:
			filestream.write(link + "\n")
		filestream.close()
	
	def login(self, login_info):
		response_s = self.session_s.post("http://puush.me/login/go", data=login_info, allow_redirects=False) # don't redirect after loggining in
		if(response_s.status_code != 302):
			print "Error while logging in. Check your credentials."
			sys.exit(1)

	def list_pools(self):
		main_page = self.session_s.get(self.base_url)
		main_page_text = main_page.text
		soup = BeautifulSoup(main_page_text)
		puush_pools_div = soup.findAll("div",attrs={"id":"puush_pools"}) # this should always return just one, so fuck for
		puush_pools_links = puush_pools_div[0].findAll("a")
		
		print "Listing pools:"
		for i in puush_pools_links:
			title = i["title"]
			href = re.sub(r"\/account\/\?pool=([0-9]+)", r"\1", i["href"]) # /account/?pool=number ==> number
			print "ID: {0} | Name: {1}".format(href, title)
		
		print "To choose a pool to dump use the \"--pool <ID>\" argument."
		print "Exiting."
		sys.exit(0)

class Downloader(object):
	"""Downloader"""
	def __init__(self, links):
		super(Downloader, self).__init__()
		self.all_links = links
		self.number_of_files = len(self.all_links)

		for i in range(0, len(self.all_links)):
			self.download_file(links[i], i+1)

	def download_file(self, url, no): # rofl?
		local_filename = "puush_files/" + url.split('/')[-1]

		r = requests.get(url, stream=True)
		length = -1

		if("content-length" in r.headers):
			if(r.headers["content-length"] != 0 or r.headers["content-length"] is not None):
				length = int(r.headers["content-length"]) or "-1"
		else:
			length = -1

		with open(local_filename, "wb") as f:
			y = 0
			perc = 0
			old_perc = -1
			for chunk in r.iter_content(chunk_size=1024): 
				if chunk: 
					try:
						y += len(chunk)
						perc = y/(length/100)
						if perc != old_perc and length != -1:
							print "Downloading file {0} out of {1}: {2}% ({3}/{4} kB)".format(no, self.number_of_files, y/(length/100), y*0.001, length*0.001)
							old_perc = perc
						elif length == -1:
							print "Downloading file {0} out of {1}: {2}% ({3}/{4} kB)".format(no, self.number_of_files, "??%", y*0.000001, "unknown")
							old_perc = 0
							perc = 0

					except ZeroDivisionError as zeroexp:
						print "Hello darkness my old friend."
					except Exception as exp:
						print "Shit happened while printing out this shitty progress info.\n{0}".format(exp)

					f.write(chunk)
					f.flush()
		return local_filename
	

class ConfigParser(object):
	"""ConfigParser class"""
	def __init__(self, args):		
		self.config_filename = args.config if args.config else "config.json"
			
		try:
			self.config_data = json.load(open(self.config_filename))
		except:					
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
		
class Arguments(argparse.ArgumentParser):
	"""Arguments class"""
	def __init__(self, *args, **kwargs):
		argparse.ArgumentParser.__init__(self, *args, **kwargs)
		print "args, kwargs: ", args, kwargs
		self.add_argument("-c", "--config", help="Alternative path to the config file. Default is ./config.json")
		self.add_argument("-o", "--output-directory", help="Override's config output folder to download to.")
		self.add_argument("-n", "--no-download", help="Don't download the files, just dump the links. Defaults to stdout, use with -f to .", action="store_true")
		self.add_argument("-f", "--text-output", help="Provide a filename to dump the links to.")
		self.add_argument("-p", "--pool", help="Change the pool (aka the puush folder) to dump. Optional, as it defaults to your selected default one on puush.me.")
		self.add_argument("-l", "--list-pools", help="Dump the list of your pools. (aka the puush folder, e.g. Private/Public/Gallery/Custom/...)", action="store_true")
	def parse(self):
		return self.parse_args()

if __name__ == "__main__":
	PuushDumper()