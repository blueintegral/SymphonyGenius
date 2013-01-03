import os, json

def list_all_files():
    directories = [d for d in os.listdir('PDFs') if 'pdf' not in d and 'DS_Store' not in d]

    fulllist = []
    add = fulllist.append

    for d in directories:
        listdir = os.listdir('PDFs/' + d)
        [add(d + ' - ' + f) for f in listdir if 'pdf' in f and 'DS_Store' not in f]
        subd = [sd for sd in listdir if 'pdf' not in sd and 'DS_Store' not in sd]
        for sub in subd:
            listsub = os.listdir('PDFs/' + d + '/' + sub)
            [add(d + ' - ' + sub + ' - ' + f) for f in listsub if 'pdf' in f and 'DS_Store' not in f]

    f = open('list.json','w')
    f.write(json.dumps(fulllist, indent=4))
    f.close()

# Copy files to full directory
def copy_files():
    from shutil import copy
    directories = [d for d in os.listdir('PDFs') if 'pdf' not in d and 'DS_Store' not in d]
    for d in directories:
        listdir = os.listdir('PDFs/' + d)
        [copy('PDFs/' + d + '/' + f, 'full/' + d + ' - ' + f) for f in listdir if 'pdf' in f and 'DS_Store' not in f]
        subd = [sd for sd in listdir if 'pdf' not in sd and 'DS_Store' not in sd]
        for sub in subd:
            listsub = os.listdir('PDFs/' + d + '/' + sub)
            [copy('PDFs/' + d + '/' + sub + '/' + f, 'full/' + d + ' - ' + sub + ' - ' + f) for f in listsub if 'pdf' in f and 'DS_Store' not in f]

def convert_to_images():
    maindir = 'full/'
    completeddir = 'symph/static/songs/'
    files = [f for f in os.listdir(maindir) if 'pdf' in f]
    for f in files:
        songdir = ''.join([c for c in f[:-4].replace(' ', '_') if c.isalnum() or c == '-' or c == '_'])
        os.system('mkdir "' + completeddir + songdir + '"')
        fname =  completeddir + songdir + '/page%03d.png'
        command = 'gs -q -dNOPAUSE -dBATCH -sDEVICE=pngmono -r150 -sOutputFile="' + fname + '" "' + maindir + f +'"'
        os.system(command)

def insert_into_db():
    import pymongo
    mongodb_url = 'mongodb://symph:symphony@ds045157.mongolab.com:45157/symph'
    connection = pymongo.Connection(mongodb_url)
    db = connection['symph']

    maindir = 'symph/static/songs/'
    files = [f for f in os.listdir(maindir) if 'DS_Store' not in f]
    for f in files:
        song = {}
        info = [t.replace('_',' ') for t in f.split('_-_')]
        song['composer'] = info[0]
        song['song'] = info[-1]
        song['bars'] = 2
        song['uploader'] = "Symphony Genius"
        song['stub'] = f
        song['images'] = [{'url':f + '/' + p} for p in os.listdir(maindir + f) if 'png' in p]
        db.songs.insert(song)

def update_db_with_sizes():
    import pymongo
    mongodb_url = 'mongodb://symph:symphony@ds045157.mongolab.com:45157/symph'
    connection = pymongo.Connection(mongodb_url)
    db = connection['symph']
    from bson import ObjectId
    import re
    import envoy
    numxnum = re.compile(r'\b\d{3,4}\sx\s\d{3,4}\b')
    sizere = re.compile(r'\b\d{3,4}\b')
    songs = db.songs.find()
    # songs = ['50c428876300f0363398f3a4', '50c428886300f0363398f68c', '50c428886300f0363398f55b', '50c428876300f0363398f282', '50c428886300f0363398f7f5', '50c428876300f0363398f3f8', '50c428886300f0363398f78d', '50c428876300f0363398f247', '50c428876300f0363398f133', '50c428886300f0363398f7e3', '50c428886300f0363398f6ec', '50c428876300f0363398f3b8', '50c428886300f0363398f7f6', '50c428886300f0363398f792', '50c428876300f0363398f14c', '50c428886300f0363398f693', '50c428876300f0363398f2ce', '50c428886300f0363398f623', '50c428886300f0363398f561', '50c428886300f0363398f544', '50c428886300f0363398f451', '50c428876300f0363398f1e0', '50c428876300f0363398f438', '50c428876300f0363398f37e', '50c428886300f0363398f46a', '50c428886300f0363398f67b', '50c428876300f0363398f37a', '50c428886300f0363398f5d4', '50c428886300f0363398f7b5', '50c428886300f0363398f6b5', '50c428886300f0363398f473', '50c428876300f0363398f225', '50c428876300f0363398f159', '50c428876300f0363398f2a1', '50c428876300f0363398f2a4', '50c428876300f0363398f2a9', '50c428886300f0363398f7c0', '50c428886300f0363398f5e5', '50c428886300f0363398f7bd', '50c428886300f0363398f5b1', '50c428886300f0363398f788', '50c428876300f0363398f1b7', '50c428876300f0363398f2ff', '50c428886300f0363398f5ed', '50c428876300f0363398f28c', '50c428886300f0363398f814', '50c428876300f0363398f13f', '50c428886300f0363398f5ba', '50c428886300f0363398f809', '50c428876300f0363398f445', '50c428886300f0363398f711', '50c428886300f0363398f625', '50c428886300f0363398f76d', '50c428886300f0363398f66c', '50c428876300f0363398f34f', '50c428876300f0363398f160', '50c428886300f0363398f728', '50c428886300f0363398f485', '50c428876300f0363398f313', '50c428876300f0363398f350', '50c428886300f0363398f675', '50c428886300f0363398f535', '50c428886300f0363398f58e', '50c428876300f0363398f182']
    for s in songs:
        song = s
        # song = db.songs.find_one({"_id":ObjectId(s)})
        if len(song['images']) > 0:
            for image in song['images']:
                filepath = "/home/ubuntu/symph/static/songs/" + image['url']
                command = "file %s" % filepath.encode('ascii', 'ignore')
                r = envoy.run(command)
                if r.status_code == 0:
                    nums = numxnum.findall(r.std_out)
                    if nums:
                        specs = sizere.findall(nums[0])
                        if len(specs) == 2:
                            image['sizes'] = {'width': specs[0], 'height': specs[1]}
                        else:
                            print song["_id"].__str__()
                    else:
                        print song["_id"].__str__()
                else:
                    print song["_id"].__str__()

            db.songs.update({"_id" : song["_id"]}, { "$set": { "images": song['images'] }})
        else:
            print "No songs for: %s" % song["_id"].__str__()

# AWS Tokens
# Public: "AKIAI3SD7IIKJVRDHUWA"
# Secret: "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"

if __name__ == '__main__':
    # list_all_files()
    # copy_files()
    # convert_to_images()
    # insert_into_db()
    update_db_with_sizes()