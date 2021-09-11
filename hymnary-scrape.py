import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
from pathlib import Path

def printArgError():
    print("""
Invalid arguments. Please supply: 
[1]: Hymnal (string), shorthand from Hymnary.org (e.g. 'UMH', 'FWS')
[2]: Hymn number to get OR first in range
[3]: Last hymn to get (optional)

e.g. python hymnary-scrape.py UMH 147 189
    """)

# Check args
if len(sys.argv) < 3 or len(sys.argv) > 4:
    printArgError()
    sys.exit()
if (not sys.argv[2].isnumeric() 
        or (len(sys.argv) == 4 
        and not sys.argv[3].isnumeric())):
    printArgError()
    sys.exit()

# Setup variables
hymnal = sys.argv[1]
startHymn = sys.argv[2]
endHymn = ""
mode = "single"
if len(sys.argv) == 4:
    endHymn = sys.argv[3]
    mode = "multiple"

if len(sys.argv) == 3:
    mode = "single"

def parseVerse(verse):
    verse = verse.replace('\t', ' ').replace('\r', '')
    p = re.compile("(?<=\d)(\.)(?!\d)")
    verse = p.sub("", verse)
    verseLines = verse.split('\n')
    verseLines = list(map((lambda verse: verse.strip()), verseLines))
    parsedVerse = '  \n'.join(verseLines)
    if re.match("Refrain:", verseLines[0]) is not None:
        parsedVerse = "*" + parsedVerse + "*"
    return parsedVerse

def checkForText(textLinks):
    if len(textLinks) == 0:
        return False

# Init webdriver
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
baseUrl = "https://hymnary.org/hymn/" + hymnal + "/"

# Check for hymnal
driver.get('https://hymnary.org/hymnal/' + hymnal)
if "does not exist" in driver.page_source:
    print("The hymnal" + "'" + hymnal + "' does not exist.")
    sys.exit()


def getHymnText(hymn):
    hymn = str(hymn)
    print(hymnal, hymn, ": Starting.")
    driver.get(baseUrl + hymn)
    if "does not exist" in driver.page_source:
        print('That hymn / hymnal does not exist')
        return
    textLinks = driver.find_elements_by_xpath("//a[@href='#text']")
    if checkForText(textLinks) is False:
        print(hymnal, hymn, ': Hymn is not available. Skipping.')
        return
    hymnTitleElem = driver.find_element_by_xpath("//h2[@class='hymntitle']")
    hymnTitleText = re.sub('\d+\. ', '', hymnTitleElem.text)
    filePath = hymnal + '/' + hymn + " " + hymnTitleText + ".txt"
    textLinks[0].click()
    licenseButton = driver.find_elements_by_xpath("//input[@class='submit-license']")
    if len(licenseButton)  != 0:
        licenseButton[0].submit()
        time.sleep(3)
    textLinks = driver.find_elements_by_xpath("//a[@href='#text']")
    textLinks[0].click()
    verses = driver.find_elements_by_xpath("//div[@id='text']//p")
    verses = list(map((lambda verse: verse.text), verses))
    parsedVerses = list(map(parseVerse, verses))
    hymnText = "\n\n".join(parsedVerses)
    file = open(filePath, 'w')
    file.write(hymnText)
    file.close()
    print(hymnal, hymn, ": Completed")
    return

# Generate list of hymns from input args
hymnToGet = []
if mode == "single":
    hymnsToGet = [startHymn]
else:
    hymnsToGet = list(range(int(startHymn), int(endHymn) + 1))

# Make dir if not already exist
Path(hymnal).mkdir(parents=True, exist_ok=True)

for hymn in hymnsToGet:
    getHymnText(hymn)

print("\nAll jobs completed!")

driver.close()
