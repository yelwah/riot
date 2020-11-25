from riotwatcher import LolWatcher
import json, os, xlsxwriter
from typing import List, Any

BLUE_TEAM, RED_TEAM = 100, 200

class Api:
  def __init__(self, apiKey, region="na1"):
    self.apiKey = apiKey
    self.watcher = LolWatcher(apiKey)
    self.region = region

def getQueueCodes(self, queueName):
  queueConversions = {
    'draft':[400],
    'solo':[420], 
    'blind':[430], 
    'flex':[440],
    'aram':[450], 
    'clash': [700] }
  queueConversions['unranked'] = [queueConversions['draft'][0], queueConversions['blind'][0]]
  queueConversions['ranked'] = [queueConversions['solo'][0], queueConversions['flex'][0]]
  queueConversions['tryhard'] = [queueConversions['solo'][0], queueConversions['flex'][0], 
    queueConversions['clash'][0]]
  if queueName == None:
    return None
  else:
    return queueConversions[queueName]

def getAccID(api, username): 
  return api.watcher.summoner.by_name(api.region, username)['accountId']

def getMatchDataPath(username): return 'match_data/' + username + ".json"

def getSavedMatches(username):
    '''Return list of dictionaries containing match information from the given users locally saved 
    matches, or an empty list if none
    '''

    print("Loading locally saved matches... ", end='', flush=True)
    try:
      with open(getMatchDataPath(username), 'r', encoding="utf-8") as saveFile:
        print("Complete. (File Loaded)", flush=True)
        return list(json.load(saveFile))
      
    except json.JSONDecodeError as e:
      print(e)
      userInput = None
      while not (userInput == 'y' or 'n'):
        userInput = input("Would you like to overwrite the current faulty file? (y/n): ")
      if userInput == "y" or userInput == "yes":
        os.remove(getMatchDataPath(username))
        print("Complete. (Erroneous File Deleted)", flush=True)
        return []
      else:
        raise
    except FileNotFoundError:
      print("Complete. (None Found)", flush=True)
      return []

def outputToExcel(filename: str, headings: List[str] = None, rowContent: List[List[Any]] = None, contentDict: List[dict] = None):
  '''Takes a list of heading names, then a list of rows contening a list of column values, and 
  outputs it to an excel file
  '''
  workbook = xlsxwriter.Workbook(filename + '.xlsx')
  worksheet = workbook.add_worksheet()

  if headings is not None and rowContent is not None:
    for i in range(len(headings)):
      worksheet.write(0, i, headings[i])

    for rowIndex in range(len(rowContent)):
      for columnIndex in range(len(rowContent[rowIndex])):
        worksheet.write(rowIndex+1, columnIndex, rowContent[rowIndex][columnIndex])

  if contentDict is not None:
    # Extract column headings
    firstDict = contentDict[0]
    column = 0
    for key in firstDict:
      worksheet.write(0, column, key)
      column += 1
  
    for row in range(len(contentDict)):
      column = 0
      for key, value in contentDict[row].items():
        worksheet.write(row+1, column, value)
        column += 1

  workbook.close()

def getChampDict():
  champDict = {}
  for filename in (os.listdir("champion")):
    with open("champion/" + filename, 'r', encoding="utf-8") as saveFile:
      championName = filename.replace('.json', "")
      champData = json.load(saveFile)
      champDict[int(champData['data'][championName]['key'])] = championName
  return champDict