import json
import os

with open('config/config.json') as json_file:
	req_data = json.load(json_file)
	req_data["auth-token"] = os.getenv("authtoken")
requireddata = req_data
roledata = {}
for roletier, roles in enumerate(req_data["tier-roles"]):
	for role in roles:
		roledata[role] = roletier+1
