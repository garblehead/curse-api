#!/usr/bin/env python3
# """API""" for curseforge
# this is a literally just a scraper for the curseforge website
# curse has no good api because drm
# (c) 2020 garblehead
# GPL-3 license
from lxml import etree
from urllib.parse import quote
import gzip
import io
import pycurl
# arbitary values
CURSE_STABLE = 0
CURSE_BETA = 1
CURSE_ALPHA = 2
# values required by curse
CURSE_DEP_REQ = 3
# try not to get captcha'd
# fake headers for linux firefox
# nss compiled curl/pycurl is required for full effectiveness
headers = ['User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Language: en-US,en;q=0.5', 'Accept-Encoding: gzip, deflate', 'Connection: keep-alive','Upgrade-Insecure-Requests: 1']

class CurseModInfo:
	def __init__(self):
		self.filename = "BadMod.def"
		self.downloadurl = "http://example.invalid/"
		self.stability = CURSE_STABLE

class CurseMod:
	def __init__(self):
		self.name = "none"
		self.game = "nada"
		self.category = "null"

# internal func
# downloads a file to a byte stream
# contains workarounds for cloudflare fuckery
def DownloadFile(url):
	page = io.BytesIO()
	page_hd = io.BytesIO()
	c = pycurl.Curl()
	c.setopt(pycurl.URL, url)
	c.setopt(pycurl.HTTPHEADER, headers)
	c.setopt(pycurl.WRITEDATA, page)
	c.setopt(pycurl.WRITEHEADER, page_hd)
	c.setopt(pycurl.FOLLOWLOCATION, True)
	c.perform()
	c.close()
	header_list = page_hd.getvalue().decode('iso-8859-1').split('\n')
	page_uc = page.getvalue()
	for i in range(0, len(header_list)-1):
		t = header_list[i].split(':')
		if(t[0].strip().lower() == 'content-encoding'):
			if(t[1].strip() == 'gzip'):
				page_uc = gzip.decompress(page.getvalue())
			elif(t[1].strip() == 'deflate'):
				raise Exception("raw deflate wtf")
			else:
				raise Exception("Unknown Content-Encoding")
	return page_uc


# internal func
# turn a bytestream to a stringio file with unix line endings
def FakeFile(string):
	return io.StringIO(string.replace(b'\r\n', b'\n').decode('utf-8'))

# returns a list of potential mod downloads, as an array of CurseModIInfo
def GetModList(game, category, mod, versions=None):
	url = "https://www.curseforge.com/"+game+"/"+category+"/"+mod+"/files/all"
	arr = []
	if versions:
		url += "?filter-game-version="+quote(versions)
	p = DownloadFile(url)
	parser = etree.HTMLParser()
	tree = etree.parse(FakeFile(p), parser)
	# TODO: gracefully handle projects without files
	filelist = tree.xpath("//table[contains(@class, 'project-file-listing')]")[0].find('tbody')
	i = 0
	for file in filelist:
		arr += [CurseModInfo()]
		e = file[0][0][0].text
		if(e == "S"): arr[i].stability = CURSE_STABLE
		elif(e == "B"): arr[i].stability = CURSE_BETA
		elif(e == "A"): arr[i].stability = CURSE_ALPHA
		e = file[1][0].text
		arr[i].filename = e
		e = file[6][0][0].attrib.get("href")
		arr[i].downloadlink = "https://www.curseforge.com"+e
		i=i+1
	return arr

# returns an array of mod name strings of required deps for given mod
def GetDependencies(game, category, mod, deptype=None):
	url = "https://www.curseforge.com/"+game+"/"+category+"/"+mod+"/relations/dependencies"
	if deptype:
		url += "?filter-related-dependencies="+deptype
	arr = []
	p = DownloadFile(url)
	parser = etree.HTMLParser()
	tree = etree.parse(FakeFile(p), parser)
	projlist = tree.xpath("//ul[contains(@class, 'project-listing')]")
	if("no-results" in projlist[0][0].attrib.get("class")): return arr
	i = 0
	for proj in projlist[0]:
		link = proj[1][0][0].attrib.get("href")
		arr += [CurseMod()]
		arr[i].game = link.split('/')[1]
		arr[i].category = link.split('/')[2]
		arr[i].name = link.split('/')[3]
		i=i+1
	return arr

# returns mod file as bytes
def DownloadMod(url):
	DownloadFile(url)
	file = DownloadFile(url+"/file")
	return file
