from PIL import Image
from cluster import HierarchicalClustering
from bson.objectid import ObjectId
import pymongo
import json
import sys
def connect_database():
    mongodb_url = 'mongodb://symph:symphony@ds045157.mongolab.com:45157/symph'
    connection = pymongo.Connection(mongodb_url)
    return connection['symph']

def get_music_bars(filename):
	musicpage = Image.open(filename)
	pixels = musicpage.load()
	width, height = musicpage.size

	imgmat = [sum([1 for x in range(width) if pixels[x,y] == 0]) for y in range(height)]

	toplines = sorted(imgmat, reverse=True)
	tophundred = toplines[0:400]
	lineguesses = [i for i, j in enumerate(imgmat) if j in tophundred]

	cl = HierarchicalClustering(lineguesses, lambda x,y: abs(x-y))
	staves = [x for x in cl.getlevel(15) if len(x) > 2]
	bands = [[min(x), max(x)] for x in staves]
	bars = [b for b in bands if b[1] - b[0] > 20]

	return bars

def update_database_bars(fileindex):
	db = connect_database()
	basepath = 'symph/static/songs/'
	filename = 'oids' + fileindex + '.json'
	fp = open(filename, 'r')
	songids = json.loads(fp.read())
	for sid in songids:
		soid = ObjectId(sid)
		song = db.songs.find_one({"_id":soid})
		print "Getting %s" % song['song']
		for image in song['images']:
			imagefile = basepath + image['url']
			bars = get_music_bars(imagefile)
			image['bars'] = bars
		db.songs.update({"_id" : soid}, { "$set": { "images": song['images'] }})

if __name__ == '__main__':
	update_database_bars(sys.argv[1])