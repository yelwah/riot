import riotapi.utilities as util
from riotapi.matchPuller import MatchPuller

class Matchup:
  def __init__(self, api: util.Api, username):
    self.username = username
    self.api = api
    self.matchData = MatchPuller.load(username)
    self.matchupDict = self.initMatchups()

  def initMatchups(self):
    matchupDict = {}
    totalChampions = 0
    for championKey in util.getChampDict():
      try:
        matchupDict[int(championKey)] = ChampMatchup(int(championKey))
        totalChampions += 1
      except:
        print("Champ key " + championKey + " failed.")
    print("Total Champions successfully added: " + str(totalChampions))
    return matchupDict

  def addMatchupResult(self, championKey: str, win: bool):
    matchup: ChampMatchup = self.matchupDict[championKey]
    matchup.wins += win
    matchup.totalMatches += 1
  
  def fillMatchups(self):
    totalwins = 0
    totallosses = 0
    for match in self.matchData:
      # Get my participant id from my summoner name
      myParticipantId = self.getParticipantId(match)

      # Get teams & winner relative to me
      enemyTeam = None
      myTeam = int(match['participants'][myParticipantId-1]['teamId'])
      myWin = match['participants'][myParticipantId-1]['stats']['win']
    
      assert(myTeam == util.BLUE_TEAM or myTeam == util.RED_TEAM)
      if myTeam == util.BLUE_TEAM:
        enemyTeam = util.RED_TEAM
      else:
        enemyTeam = util.BLUE_TEAM
      if myWin:
        myWin = 1
        totalwins += 1
      else:
        myWin = 0
        totallosses += 1
      assert(myWin == 0 or myWin == 1)

      # Add champion matchup data to me for each enemy player
      for participant in match['participants']:
        if int(participant["teamId"]) == enemyTeam:
          self.matchup.addMatchupResult(int(participant['championId']), myWin)

class ChampMatchup:
  champDict = util.getChampDict()

  def __init__(self, enemyChampionKey):
    self.enemyChampion = enemyChampionKey
    self.name = ChampMatchup.champDict[enemyChampionKey]
    self.wins = 0
    self.totalMatches = 0
    # self.myChampion = ChampMatchup.champDict[myChampionKey]
  
  def getWinningPct(self):
    try:
      return (100 * (self.wins/self.totalMatches))
    except ZeroDivisionError:
      return -1
  
  def getLosses(self): return self.totalMatches - self.wins