#!/usr/bin/env python
# (c) 2020 garblehead
# gpl-3
import cursescrape
import io
import json

class VerEncJson(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, cursescrape.CurseVersionType):
			return {"name": obj.name, "id": obj.id, "list": obj.list}
		elif isinstance(obj, cursescrape.CurseVersion):
			return {"name": obj.name, "id": obj.id}
		return json.JSONEncoder.default(self, obj)

versions = cursescrape.GetVersionList("minecraft", "mc-mods")
fh = io.open("vertable.json", "w+")
json.dump(versions, fh, cls=VerEncJson)
fh.close()
