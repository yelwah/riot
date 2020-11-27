import riotapi.utilities as util

class Match:
  def __init__(self, rawMatchDetails):
    self.rawMatchDetails = rawMatchDetails
    self.participants = self.getParticipants(rawMatchDetails)
    self.players = []
    self.fillPlayers()
  
  def getParticipants(self, rawMatchDetails):
    participantDict = {}
    for participant in rawMatchDetails['participantIdentities']:
      participant[participant['player']['summonerName']] = participant['participantId']
    return participantDict
  
  def fillPlayers(self):
    for participantId, username in self.participants.items():
      self.players.append(Player(username, participantId))

class Player:
  def __init__(self, username, participantId):
    self.username = username
    self.pid = participantId
    self.rawMatchDetails = self.rawMatchDetails
    self.parsePlayerStats()

  def getParticipantData(self):
    for p in self.rawMatchDetails:
      if p['participantId'] == self.pid:
        return p

  def getRole(self, participantTimelineData):
    riotRole = participantTimelineData['role']
    lane = participantTimelineData['lane']

    if riotRole == "DUO_SUPPORT":
      return "SUPPORT"
    else:
      return lane

  def parsePlayerStats(self):
    pData   = self.getParticipantData()
    pStats  = pData['stats']
    pTL     = pData['timeline']

    self.win        = bool(pStats['win'])
    self.champion   = util.CHAMPIONS[pData['champId']]
    self.kills      = int(pStats['kills'])
    self.deaths     = int(pStats['deaths'])
    self.assists    = int(pStats['assists'])
    self.cs         = int(pStats['totalMinionsKilled'])
    self.cspm0to10  = float(pTL['creepsPerMinDeltas']['0-10'])
    self.cspm10to20 = float(pTL['creepsPerMinDeltas']['10-20'])
    self.items      = []
    for i in range(7):
      key = 'item' + str(i)
      self.items.append(util.ITEMS[pStats[key]])    
    self.dmgToChamp = int(pStats['totalDamageDealtToChampions'])
    self.mgatedDmg  = int(pStats['damageSelfMitigated'])
    self.dmgTaken   = int(pStats['totalDamageTaken'])
    self.healing    = int(pStats['totalHeal'])
    self.visionScr  = int(pStats['visionScore'])
    self.lane       = self.getRole(pTL)
  
  def __str__(self):
    matchResult = "Loss"
    if self.win:
      matchResult = "Win"
    
    itemString = ''
    for i in range(len(self.items)):
      if i != 0:
        itemString += ', '
      itemString += self.item[i]

    return(
      self.username + ", " + self.champion + ": " + matchResult + '\n' + 
      str(self.kills) + ' / ' + str(self.deaths) + ' / ' + self.assists + ' | CS: ' + self.cs + '\n' + 
      'Items: ' + itemString
    )
