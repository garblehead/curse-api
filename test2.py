#!/usr/bin/env python
# (c) 2020 garblehead
# gpl-3
import cursescrape
import io

modl = cursescrape.GetModList("minecraft", "mc-mods", "rftools")
info = cursescrape.GetModFileInfo("minecraft", "mc-mods", "rftools", modl[0].fileid)
for dep in info.dependencies:
	print(dep.name)
