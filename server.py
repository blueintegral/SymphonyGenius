import os, random, string, base64
from flask import Flask, render_template, jsonify, request
from bson.objectid import ObjectId
import cloudinary
from cloudinary import uploader
import subprocess
app = Flask(__name__)

cloudinary.config(  
    cloud_name = 'hkywxh2wq',
    api_key = '198533153838981',
    api_secret = 'HXiYg-S4kw8y53rGeRdzJVTCw_Q'
)

# MongoDB Database Setup
import pymongo
def connect_database():
    mongodb_url = 'mongodb://symph:symphony@ds045157.mongolab.com:45157/symph'
    connection = pymongo.Connection(mongodb_url)
    return connection['symph']

db = connect_database()

songindex = db.songs.find()
SONG_CACHE = [s for s in songindex if s['images'][0].get('bars',False) and s['images'][0].get('sizes',False)]

@app.route("/")
def index():
    return render_template('index.html', songs=SONG_CACHE)

@app.route("/example")
def example():
    return render_template('/example.html')

@app.route("/id/<songid>")
def songid(songid):
    mongoid = ObjectId(songid)
    song = db.songs.find_one({"_id" : mongoid})
    comments = db.comments.find({"data.songid" : songid})
    images = song.get('images')
    sizes = song.get('sizes', {"width":1245,"height":1619})
    width = max([int(x['sizes']['width']) for x in images])
    height = sum([int(x['sizes']['height']) for x in images])
    offsets = [sum([int(x['sizes']['height']) for x in images][0:i]) for i in range(len(images))]
    commentData = []
    for c in comments:
        data = c['data']
        data['commentid'] = str(c['_id'])
        commentData.append(data)
    if len(images) > 0:
        images = sorted(images, key=lambda x: x['url'])
    return render_template('song.html', song=song, comments=commentData, images=images, sizes=sizes, height=height, width=width, offsets=offsets)

@app.route("/id/<songid>/comment", methods = ['GET','POST'])
def newComment(songid):
    if request.method == 'POST':
        requestJson = request.json
        postJson = {'data':requestJson}
        postJson['data']['songid'] = songid
        postJson['data']['commentid'] = str(db.comments.insert(postJson))
        respdict = {"success":True, "data":postJson['data']}
        resp = jsonify(respdict)
        resp.status_code = 200
        return resp

@app.route("/id/<commentid>/vote", methods = ['GET','POST'])
def voteUp(commentid):
    if request.method == 'POST':
        postJson = request.json # actually not used. Will need when users implemented...
        mongoid = ObjectId(commentid)
        db.comments.update({"_id" : mongoid}, { "$inc": { "data.votes": 1}})
        respdict = {"success":True}
        resp = jsonify(respdict)
        resp.status_code = 200
        return resp

@app.route("/upload", methods = ['GET','POST'])
def upload():
    if request.method == 'POST':
        postJson = request.json
        # Object has filename, key, mimetype, size & url
        result = convert(postJson)
        if result:
            respdict = {"success":True, "data":result}
        else:
            respdict = {"success":False}
        resp = jsonify(respdict)
        resp.status_code = 200
        return resp

def convert(jsonData):
    fileURL = jsonData['files'][0]['url']
    randID = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(10))
    try:
        wgetOutput = subprocess.check_output('wget -O temp/'+randID+'.mid '+fileURL, shell=True)
        midilyOutput = subprocess.check_output('midi2ly -o temp/ temp/'+randID+'.mid', stderr=subprocess.STDOUT, shell=True)
        app.logger.info("Midi2ly Output: %s" % midilyOutput)
        if "expect bad output" in midilyOutput:
            return False
        lilypondOutput = subprocess.check_output('lilypond -f png -o temp/output temp/'+randID+'-midi.ly', stderr=subprocess.STDOUT, shell=True)
        app.logger.info("lilypond Output: %s" % lilypondOutput)
        rmMidiOutput = subprocess.check_output('rm temp/output/'+randID+'-midi.midi', shell=True)
        lsFilesOutput = subprocess.check_output('ls temp/output/ > list.txt', shell=True)
        rmLyOutput = subprocess.check_output('rm temp/'+randID+'-midi.ly', shell=True)
        midiToWav(randID+'.mid')
        mvMidiOutput = subprocess.check_output('mv temp/'+randID+'.mid static/midi', shell=True)
    except subprocess.CalledProcessError:    
        return False
    else:
        filenames = open('list.txt','r').readlines()
        imageData = []
        for i in filenames:
            result = uploader.upload('temp/output/'+i.rstrip('\n'))
            imageData.append(result)
            rmTempFilesOutput = subprocess.check_output('rm temp/output/'+i.rstrip('\n'), shell=True)
        jsonData['images'] = imageData
        jsonData['data'] = midiTo64('static/midi/'+randID+'.mid')
        jsonData['randID'] = randID
        jsonData['usergenerated'] = True
        response = db.songs.insert(jsonData)
        jsonData['id'] = str(response)
        return jsonData

def midiTo64(file):
    line = open(file, 'r').readline()
    encoded = base64.b64encode(line)
    return encoded

def midiToWav(file):
    fluidsynthOutput = subprocess.check_output('fluidsynth -F static/wav/'+file+'.wav /usr/share/sounds/sf2/FluidR3_GM.sf2 temp/'+file, shell=True)

def test():
    midilyOutput = subprocess.check_output('midi2ly -o temp/ temp/test.mid', stderr=subprocess.STDOUT, shell=True)
    if "expect bad output" in midilyOutput:
        return False
    try:
        lilypondOutput = subprocess.check_output('lilypond -f png -o temp/output temp/test-midi.ly', stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError:    
        return False
    if "expect bad output" in lilypondOutput:
        return False
    else:
        return True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = os.environ.get('DEBUG', True)
    app.logger.info("Debug is set to: %s" % app.debug)
    app.run(host='0.0.0.0', port=port)
