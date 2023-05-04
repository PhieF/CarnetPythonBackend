

from zipfile import ZipFile
import re
from .html2text import html2text
import json
import os
import random
import string
import time;
from .metadata import Metadata
from .settings_manager import *
import shutil
from pathlib import Path

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        if(item.endswith(".swp")):
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

class NoteManager():

    def __init__(self, notePath=None):
        self.notePath = notePath

        Path(self.notePath).mkdir( parents=True, exist_ok=True )

    def getMetadata(self):
        try:
            if os.path.isfile(self.notePath):
                with ZipFile(self.notePath) as zipnote:
                    try:
                        with zipnote.open('metadata.json') as meta:
                            ret = {}
                            ret['metadata'] = json.loads(meta.read().decode("utf-8"))
                            with zipnote.open('index.html') as index:
                                ret['shorttext'] = html2text(index.read().decode("utf-8")).strip()[0:150]
                                return ret
                    except KeyError:
                        try:
                            with zipnote.open('index.html') as index:
                                ret['shorttext'] = html2text(index.read().decode("utf-8")).strip()[0:150]
                                return ret
                        except KeyError:
                            return None
            else:

                ret = {}
                file = open(self.notePath+"/metadata.json", 'r')
                text = file.read()
                file.close()
                ret['metadata'] = json.loads(text)
                file = open(self.notePath+"/note.md", 'r')
                text = file.read()
                file.close()
                ret['shorttext'] = html2text(text).strip()[0:150]
                return ret
        except FileNotFoundError:
            return None
    def getCachedMetadata(self):
        #self.loadCache()
        return self.getMetadata()
    #returns html + metadata

    def saveTextAndMetadataToOpenedNote(self, text, metadatastr, tmp_path):

        index  = open(tmp_path+"/index.html", "w")
        index.write(text)
        index.close()
        metadata  = open(tmp_path+"/metadata.json", "w")
        metadata.write(metadatastr)
        metadata.close()
        self.saveCurrentNote(tmp_path)

    def saveCurrentNote(self, tmp_path):
        if os.path.isfile(self.notePath):
            zip_ref = ZipFile(self.notePath+".tmp", 'w')
            self.zipdir(tmp_path, zip_ref)
            zip_ref.close()
            try:
                os.remove(self.notePath)
            except FileNotFoundError:
                None
            os.rename(self.notePath+".tmp", self.notePath)
        else:
            if(not os.path.exists(self.notePath)):
                os.makedirs(self.notePath)
            copytree(tmp_path, self.notePath)


    #return path of the new note
    def createNewNote(self, relative_dir, tmp_extract_path):

        i=0
        path = relative_dir
        files = os.listdir(settingsManager.getNotePath()+"/"+path)
        ret = []
        basename = ""
        found = False
        while(not found):
            basename = "untitled"
            if(i>0):
                basename = basename + " " + str(i)
            found = True
            for name in files:

                if(name.startswith(basename)):
                    found = False
                    break
            i = i+1
        basename = basename + ''.join(random.choice(string.ascii_uppercase) for x in range(2))+".sqd"
        self.notePath = path + "/" + basename
        content = ""
        os.makedirs(tmp_extract_path)
        index  = open(tmp_extract_path+"/note.md", "w")
        index.write(content)
        index.close()
        metadata = Metadata()
        metadata.creation_date = int(time.time() * 1000)
        metadata.last_modification_date = metadata.creation_date

        metadataFile  = open(tmp_extract_path+"/metadata.json", "w")
        metadataFile.write(metadata.toString())
        metadataFile.close()

        return self.notePath

    #return path of the new note
    def createNewNoteHTML(self, relative_dir, tmp_extract_path):
        
        i=0
        path = relative_dir
        files = os.listdir(settingsManager.getNotePath()+"/"+path)
        ret = []
        basename = ""
        found = False
        while(not found):
            basename = "untitled"
            if(i>0):
                basename = basename + " " + str(i)
            found = True
            for name in files:

                if(name.startswith(basename)):
                    found = False
                    break
            i = i+1
        basename = basename + ''.join(random.choice(string.ascii_uppercase) for x in range(2))+".sqd"
        self.notePath = path + "/" + basename
        content = "<div id=\"text\" contenteditable=\"false\">\
         <!-- be aware that THIS will be modified in java -->\
         <div class=\"edit-zone\" contenteditable=\"true\" dir=\"auto\">\
         </div></div><div id=\"floating\"></div>"
        os.makedirs(tmp_extract_path)
        index  = open(tmp_extract_path+"/index.html", "w")
        index.write(content)
        index.close()
        metadata = Metadata()
        metadata.creation_date = int(time.time() * 1000)
        metadata.last_modification_date = metadata.creation_date

        metadataFile  = open(tmp_extract_path+"/metadata.json", "w")
        metadataFile.write(metadata.toString())
        metadataFile.close()

        return self.notePath

    def zipdir(self, path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), os.path.join(root[len(path):], file))

    def extractNote(self, to):
        import shutil
        try:
            shutil.rmtree(to)
        except FileNotFoundError:
            print ("not found")
        os.makedirs(to)
        self.lastExtractedDest = to
        ret = {}
        if os.path.isfile(self.notePath):
            zip_ref = ZipFile(self.notePath, 'r')
            zip_ref.extractall(to)
            zip_ref.close()
        else:
            copytree(self.notePath, to)
        try:
            file = open(to+"/metadata.json", 'r')
            text = file.read()
            file.close()
            ret['metadata'] = json.loads(text)
        except FileNotFoundError:
            ret['metadata'] = {}

        try:
            file = open(to+"/index.html", 'r')
            text = file.read()
            file.close()
            ret['html'] = text
        except FileNotFoundError:
            ret['html'] = ""
        return ret
