import json
from discord import Embed

data = [{}]
def setup(fileName):
	global data
	with open(fileName) as file:
		data = json.loads(file.read())
	
def unitExists(id):
	try:
		assert data[id]  # todo write this in another way
		return True
	except KeyError:
		return False

def makeEmbedFromUnit(id):  # if we are here we expect the unit to exist
	emb = Embed(description='UDP of ' + data[id]['Name'], color=0xffffff)
	emb.set_author(name='Cat Bot')
	emb.add_field(name='Brief description', value=data[id]['Description'][0] +
			' [Click here for more](https://thanksfeanor.pythonanywhere.com/UDP/' + id.zfill(3) + ')', inline=False)
	# uncomment to make feanor angry
	# emb.set_image(url='https://thanksfeanor.pythonanywhere.com/static/UDPCards/UDPCARD'+id+'.png')
	return emb
