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
		self.filename = None
		self.fileid = None
		self.stability = None
		self.dependencies = None

class CurseMod:
	def __init__(self):
		self.name = "none"
		self.game = "nada"
		self.category = "null"

# internal func
# downloads a file to a byte stream
# contains workarounds for cloudflare fuckery
def __file_dl(url):
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

def __file_local():
	fp = io.open(None, "rb")
	data = fp.read()
	fp.close()
	return data

# internal func
# turn a bytestream to a stringio file with unix line endings
def __file_fake(string):
	return io.StringIO(string.replace(b'\r\n', b'\n').decode('utf-8'))

# more internals
def __stability_set(e):
	if(e == "R"): return CURSE_STABLE
	elif(e == "B"): return CURSE_BETA
	elif(e == "A"): return CURSE_ALPHA

def __get_mod_from_url(url):
	mod = CurseMod()
	spurl = url.split('/')
	mod.game = spurl[1]
	mod.category = spurl[2]
	mod.name = spurl[3]
	return mod

# returns CurseModInfo with more details, like accurate filename and dep info
def GetModFileInfo(game, category, mod, fileid):
	url = "https://www.curseforge.com/"+game+"/"+category+"/"+mod+"/files/"+fileid
	info = CurseModInfo()
	p = __file_dl(url)
	parser = etree.HTMLParser()
	tree = etree.parse(__file_fake(p), parser)
	info.fileid = fileid
	# quite a fuzzy match
	try:
		infohtml = tree.xpath("//article[contains(@class, 'box')]")[0]
		e = infohtml[0][0][0][0][0].text
		info.stability = __stability_set(e)
		info.filename = infohtml[1][0][1].text
		info.dependencies = []
		dephtml = tree.xpath("//section[contains(@class, 'items-start')]")
		# find the dependency info
		i = 0
		deplist = None
		for f in dephtml:
			if not(len(dephtml[i])):
				i=i+1
				break
			if(dephtml[i][0].text == "Required Dependency"):
				deplist = dephtml[i]
				break
			i=i+1
		if(deplist is not None):
			for dep in deplist[1]:
				info.dependencies += [__get_mod_from_url(dep[0][1][0][0].attrib.get("href"))]
	except:
		print(etree.tostring(tree).decode('utf-8'))
		raise
	return info

# returns a list of potential mod downloads, as an array of CurseModIInfo
def GetModList(game, category, mod, versions=None):
	url = "https://www.curseforge.com/"+game+"/"+category+"/"+mod+"/files/all"
	arr = []
	if versions:
		url += "?filter-game-version="+quote(versions)
	p = __file_dl(url)
	parser = etree.HTMLParser()
	tree = etree.parse(__file_fake(p), parser)
	# TODO: gracefully handle projects without files
	filelist = tree.xpath("//table[contains(@class, 'project-file-listing')]")[0].find('tbody')
	i = 0
	for file in filelist:
		arr += [CurseModInfo()]
		e = file[0][0][0].text
		arr[i].stability = __stability_set(e)
		e = file[1][0].attrib.get("href")
		arr[i].fileid = e.split('/')[5]
		e = file[1][0].text #donot trust, no file extension typically
		arr[i].filename = e
		arr[i].downloadlink ="https://www.curseforge.com/"+game+"/"+category+"/"+mod+"/download/"+arr[i].fileid
		i=i+1
	return arr

# returns an array of mod name strings of required deps for given mod
def GetDependencies(game, category, mod, deptype=None):
	url = "https://www.curseforge.com/"+game+"/"+category+"/"+mod+"/relations/dependencies"
	if deptype:
		url += "?filter-related-dependencies="+deptype
	arr = []
	p = __file_dl(url)
	parser = etree.HTMLParser()
	tree = etree.parse(__file_fake(p), parser)
	projlist = tree.xpath("//ul[contains(@class, 'project-listing')]")
	if("no-results" in projlist[0][0].attrib.get("class")): return arr
	i = 0
	for proj in projlist[0]:
		link = proj[1][0][0].attrib.get("href")
		arr += [__get_mod_from_url(link)]
		i=i+1
	return arr

# returns mod file as bytes
def DownloadMod(game, category, mod, fileid):
	url="https://www.curseforge.com/"+game+"/"+category+"/"+mod+"/download"+fileid
	__file_dl(url)
	file = __file_dl(url+"/file")
	return file
