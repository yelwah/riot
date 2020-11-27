from riotwatcher import LolWatcher
import json, os

BLUE_TEAM, RED_TEAM = 100, 200

def getApiKey():
  key = ''
  with open('apikey.txt', 'r', encoding="utf-8") as file:
    key = file.readline()
  return key

class Api:
  def __init__(self, region="na1"):
    self.apiKey = getApiKey()
    self.watcher = LolWatcher(self.apiKey)
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

def getChampDict():
  champDict = {}
  for filename in (os.listdir("static_data/champion")):
    with open("static_data/champion/" + filename, 'r', encoding="utf-8") as saveFile:
      championName = filename.replace('.json', "")
      champData = json.load(saveFile)
      champDict[int(champData['data'][championName]['key'])] = championName
  return champDict
CHAMPIONS = getChampDict()

def getItemDict():
  itemDict = {}
  with open("static_data/item.json", 'r', encoding="utf-8") as saveFile:
    rawItemData = json.load(saveFile)
    for key, value in rawItemData['data'].items():
      itemDict[int(key)] = value['name']
    return itemDict
ITEMS = getItemDict()