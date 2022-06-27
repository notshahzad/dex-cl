import subprocess
import requests
import keyboard
from wand.image import Image
import struct, fcntl,termios

def fetchChapter(chapterid):
    global baseurl,panelurls
    pages = requests.get(f'https://api.mangadex.org/at-home/server/{chapterid}',headers={'accept':'application/json'})
    pages = pages.json()
    panelurls[chapterid] = {} 
    baseurl = pages['baseUrl']
    panelurls[chapterid]['hash'] = pages['chapter']['hash']
    for i in range(0,len(pages['chapter']['data'])):
        panelurls[chapterid][pages['chapter']['data'][i].split("-")[0]] = pages['chapter']['data'][i]
        # print(panelurls)

def displayPanel(image):
    global hw
    ratio = image['w'] / image['h']
    displaywidth = int( ratio * hw[3] )
    print(image['h'],image['w'],hw[3],displaywidth,ratio)
    with Image(blob=image['data']) as img:
        img.resize(height=hw[3],width=displaywidth)
        currentimage = img.make_blob('jpg')
    subprocess.run(["/usr/bin/kitty", "icat" , "--clear"])
    subprocess.run([ "/usr/bin/kitty", "icat"], input=currentimage) 

def fetchPanel(url):
    imageid = url.split("/")
    imageid = imageid[len(imageid)-1].split(".")[0]
    if imageid in images:
        if len(images[imageid]):
            displayPanel(images[imageid])
            return
    image = requests.get(url)
    image = image.content
    images[imageid] = {}
    with Image(blob=image) as img:
        images[imageid]['h'] = img.height
        images[imageid]['w'] = img.width
    images[imageid]['data'] = image
    displayPanel(images[imageid])

def FetchManga(mangaid):
    global language, chapters
    chaps = requests.get(f'https://api.mangadex.org/manga/{mangaid}/aggregate?translatedLanguage[]={language}',headers={'accept':'application/json'})
    chaps = chaps.json()
    if not len(chaps['volumes']):
        print("no chapters found")
        return -1
    # print(chaps['volumes'])
    chapters[mangaid] = {}
    for i in chaps['volumes']:
        for j in chaps['volumes'][i]['chapters']:
            chapters[mangaid][j] = chaps['volumes'][i]['chapters'][j]['id']

currentchapter = "484088b5-dc50-476e-9576-a6db27960116"
chapter = 14
currentpanel = 1
reading = True
language = 'en'
chapters = {}
panelurls = {}
baseurl = ""
images = {}
s = struct.pack('HHHH',0,0,0,0)
hw = fcntl.ioctl(1,termios.TIOCGWINSZ,s)
hw = struct.unpack('HHHH',hw)
FetchManga(currentmanga)
fetchChapter(chapters[currentmanga][f'{chapter}'])
while 1:
    while 1:
        if reading:
            if currentpanel == 1:
                url = baseurl+"/data/"+panelurls[chapters[currentmanga][f'{chapter}']]['hash']+"/"+panelurls[chapters[currentmanga][f'{chapter}']][f'{currentpanel}']
                fetchPanel(url)
            if (keyboard.is_pressed("q")):
                exit()
            if (keyboard.is_pressed("h") and currentpanel > 1):
                currentpanel -= 1
                url = baseurl+"/data/"+panelurls[chapters[currentmanga][f'{chapter}']]['hash']+"/"+panelurls[chapters[currentmanga][f'{chapter}']][f'{currentpanel}']
                fetchPanel(url)
                break
            if keyboard.is_pressed("l") and currentpanel < len(panelurls[chapters[currentmanga][f'{chapter}']]):
                currentpanel += 1
                url = baseurl+"/data/"+panelurls[chapters[currentmanga][f'{chapter}']]['hash']+"/"+panelurls[chapters[currentmanga][f'{chapter}']][f'{currentpanel}']
                fetchPanel(url)
                break

