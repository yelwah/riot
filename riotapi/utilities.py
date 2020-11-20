from riotwatcher import LolWatcher,

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
  return queueConversions[queueName]

def getAccID(self, summonerName, region='na1'): 
  return self.api.watcher.summoner.by_name(region, summonerName)['accountId']
