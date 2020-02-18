#!/usr/bin/env python
# (c) 2020 garblehead
# gpl-3
import cursescrape
import io

def downloadMod(game, category, mod, version=None):
	modl = cursescrape.GetModList(game, category, mod, version)
	for file in modl:
		if(file.stability == cursescrape.CURSE_STABLE):
			todl = file.fileid
			break
	file = cursescrape.GetModFileInfo(game, category, mod, todl)
	fh = io.open(file.filename, "wb+")
	fh.write(cursescrape.DownloadMod(game, category, mod, todl))
	fh.close()
	for dep in file.dependencies:
		downloadMod(dep.game, dep.category, dep.name, version)

downloadMod("minecraft", "mc-mods", "rftools", "1738749986:5") # 1.7.10
