from riotwatcher import LolWatcher, ApiError
import json, os, time

def getChampDict():
  champDict = {}
  for filename in (os.listdir("champion")):
    with open("champion/" + filename, 'r', encoding="utf-8") as saveFile:
      championName = filename.replace('.json', "")
      champData = json.load(saveFile)
      champDict[int(champData['data'][championName]['key'])] = championName
  return champDict

champDict = getChampDict()

class Api:
  def __init__(self, apiKey, region="na1"):
    self.apiKey = apiKey
    self.watcher = LolWatcher(apiKey)
    self.region = region

class Player:
  def __init__(self, api: Api, name):
    self.name = name
    self.api = api
    self.summoner = None
    self.accId = None
    self.iconId = None
    self.level = None
    self.initPlayer()
    self.matchData = MatchData(self.api, self)
    self.matchups = self.initMatchups()

  def initPlayer(self):
    try:
      self.summoner = self.api.watcher.summoner.by_name(self.api.region, self.name)
      self.accId = self.summoner['accountId']
      self.iconId = self.summoner['profileIconId']
      self.level = self.summoner['summonerLevel']
    except ApiError as e:
      print("Error while interfacing with the API attempting to construct a Player object.")
      print(e)

  def initMatchups(self):
    matchupDict = {}
    totalChampions = 0
    for championKey in champDict:
      try:
        matchupDict[int(championKey)] = ChampMatchup(int(championKey))
        totalChampions += 1
      except:
        print("Champ key " + championKey + " failed.")
    print("Total Champions successfully added: " + str(totalChampions))
    return matchupDict

  def addMatchupResult(self, championKey: str, win: bool):
    matchup: ChampMatchup = self.matchups[championKey]
    matchup.wins += win
    matchup.totalMatches += 1

class MatchData:
  def __init__(self, api: Api, player: Player):
    self.api = api
    self.player = player
    self.filename = "match_data_" + player.name + ".json"
    self.matchDetailData = self.getSavedMatches()

  def getSavedMatches(self):
    # Check the most recent match in locally saved matches
    try:
      with open(self.filename, 'r', encoding="utf-8") as saveFile:
        return json.load(saveFile)
    except json.JSONDecodeError as e:
      print(e)
      userInput = None
      while not (userInput == 'y' or 'n'):
        userInput = input("Would you like to overwrite the current faulty file? (y/n): ")
      if userInput == "y":
        os.remove(self.filename)
        return []
      else:
        raise
    except FileNotFoundError:
      return []
    
  def updateMatchData(self):
    print("================================================================================")
    print("Updating " + self.player.name + "'s match history...")
    oldMatchDetailData = self.matchDetailData
    newMatchData = self.api.watcher.match.matchlist_by_account(
        region = self.api.region, 
        encrypted_account_id = self.player.accId
        , queue = [420,440]
        , begin_index = 1
        , end_index = 2
        # , champion = [103]
        )
    print(type(newMatchData))
    print(newMatchData)
    if oldMatchDetailData:
      mostRecentMatchId = oldMatchDetailData[-1]['gameId']
    else:
      mostRecentMatchId = False
    newMatchDetailData = []
    totalTime = newMatchesAdded = matchesAccessed = 0
    matchesErrored = 0
    print("[", end="")
    with open(self.filename, 'w', encoding="utf-8") as outfile: 
      # for matchIndex in range(98, 0, -1):
      for matchIndex in range(newMatchData['startIndex'], newMatchData['endIndex']-1):
        time.sleep(0.05) # Prevent from requesting API too much

        startTime = time.time() # start recording time of this iteration
        print("=", end="", flush=True) # progress bar

        # Set current match from index or break if fully updated
        if mostRecentMatchId:
          if newMatchData['matches'][matchIndex]['gameId'] == mostRecentMatchId:
            break
        currMatch = newMatchData['matches'][matchIndex]

        # Fetch match details on ranked games
        soloQ, flexQ = 420, 440
        if currMatch['queue'] == soloQ or currMatch['queue'] == flexQ:
          try:
            matchDetail = self.api.watcher.match.by_id(self.api.region, currMatch['gameId'])
          except:
            matchesErrored += 1
            continue
          newMatchDetailData.append(matchDetail)
          newMatchesAdded += 1
        matchesAccessed += 1

        totalTime = totalTime + (time.time()-startTime) # add elapsed time from this iteration to total
      print("]", end="")
      if newMatchesAdded == 0:
        print("\r", end="")
      else: 
        print()
      try: 
        averageTime = totalTime/matchesAccessed
        print("Success! Avg access time/match = " + str(averageTime) + " seconds")
      except:
        pass

      # Orient list from old to new, save updated match data to object & file
      self.matchDetailData = oldMatchDetailData + newMatchDetailData
      json.dump(self.matchDetailData, outfile)   
        
      print(str(newMatchesAdded) + " new matches added to save file." + str(matchesErrored) + " matches errored out.")
      print("================================================================================")

class ChampMatchup:
  def __init__(self, key):
    self.key = key
    self.name = champDict[key]
    self.wins = 0
    self.totalMatches = 0
  
  def getWinningPct(self):
    try:
      return (100 * (self.wins/self.totalMatches))
    except ZeroDivisionError:
      return -1
  
  def getLosses(self): return self.totalMatches - self.wins