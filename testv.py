#!/usr/bin/env python
# (c) 2020 garblehead
# gpl-3
import cursescrape
import io

versions = cursescrape.GetVersionList("minecraft", "mc-mods")
for version in versions:
	print(version.name+" i "+version.id)
