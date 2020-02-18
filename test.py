#!/usr/bin/env python
# (c) 2020 garblehead
# gpl-3
import cursescrape
import io

def writeMod(mod):
	modl = cursescrape.GetModList("minecraft", "mc-mods", mod)
	for file in modl:
		if(file.stability == cursescrape.CURSE_STABLE):
			todl = file.downloadlink
			filename = file.filename
			break

	content = cursescrape.DownloadMod(todl)
	fh =  io.open(filename+".jar", "wb+")
	fh.write(content)
	fh.close()

writeMod("rftools")
deps = cursescrape.GetDependencies("minecraft", "mc-mods", "rftools", "3")
for dep in deps:
	writeMod(dep.name)
