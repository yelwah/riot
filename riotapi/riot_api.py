from riotapi import utilities, updateMatchData
from riotwatcher import ApiError

class Matchup:
  def __init__(self, api: utilities.Api, username):
    self.username = username
    self.api = api
    self.matchData = utilities.getSavedMatches(username)
    self.matchupDict = self.initMatchups()

  def initMatchups(self):
    matchupDict = {}
    totalChampions = 0
    for championKey in utilities.getChampDict():
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

class ChampMatchup:
  champDict = utilities.getChampDict()

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