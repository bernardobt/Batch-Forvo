from aqt import mw
from anki.hooks import addHook
from aqt.qt import *
from aqt.utils import showInfo

from .AnkiAudioTools import languages, download_Audio, AnkiAudioGlobals, AnkiAudioObject
import os
import glob

from . import bs4Scraper as scraper

# Load config json
config = mw.addonManager.getConfig(__name__)
field_to_add = config['field_to_add']
field_to_read = config['field_to_read']
shortcut = config['shortcut']
languageCode = config['languageCode']
downloadPath = config['downloadPath']

def deleteTempFiles():
        for tempFile in glob.glob(downloadPath + AnkiAudioGlobals.TEMP_FILE_PREFIX + '*'):
            os.remove(tempFile)

def insertIntoCard(ankiAudioObject, note):
        #select the forvo audio to add. 
        fullpath = downloadPath + AnkiAudioGlobals.TEMP_FILE_PREFIX + ankiAudioObject.getBucketFilename()
        if(os.path.isfile(fullpath)): # if it was a temp file, rename it
            os.rename(fullpath, downloadPath + ankiAudioObject.getBucketFilename())
        else: # else download it without temp prefix
            download_Audio(ankiAudioObject.word, ankiAudioObject.link, downloadPath, ankiAudioObject.getBucketFilename())
        deleteTempFiles() #TODO: maybe in seperate thread
        if note[field_to_add] == "": 
            note[field_to_add] += f"[sound:{ankiAudioObject.getBucketFilename()}]"

def find_audio(note):
    results = scraper.lookup_word(note[field_to_read], languageCode.split("_")[1])
    if(len(results) != 0):
        insertIntoCard(results[0], note)

# Detect selected cards in browser
def show_selected_from_browser(nids):
    for id in nids:
        note = mw.col.getNote(id)
        find_audio(note)
        note.flush()
        mw.reset()
    showInfo(f"Finished Process")

# Create a new menu item, "Batch Add Forvo"
def setupMenu(browser):
    action = QAction(f'Batch Add Forvo Audio', browser)
    action.setShortcut(shortcut)
    action.triggered.connect(lambda: onRegenerate(browser, field_to_read))
    browser.form.menuEdit.addAction(action)

def onRegenerate(browser, field):
    show_selected_from_browser(browser.selectedNotes())

addHook("browser.setupMenus", setupMenu)