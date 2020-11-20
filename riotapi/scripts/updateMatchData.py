from riotwatcher import LolWatcher, ApiError
from riotapi import utilities as riotUtil
import json, time, sys, os
from typing import Set
username = sys.argv[1]

class MatchUpdater():
  def __init__( self,
                api:            riotUtil.Api,
                username:       str, 
                stop:           int, 
                start:          int = 0, 
                champions: Set[int] = None,
                queue:          str = None):
    self.api = api
    self.username = username
    self.accID = riotUtil.getAccID(username, api.region)
    self.region = api.region
    self.start, self.stop = start, stop
    self.champions = champions
    self.queueCodes = riotUtil.getQueueCodes(queue)
    self.relativePath = '/match_history/' + username + ".json"
  

  def pullMatchList(self):
    '''Return a List of Dictionaries with basic match data for a sequence of matches with specific
    account name'''
    print("Pulling " + username + "'s match list... ", end='')

    matchlist: Set[dict] = []
    for chunkStart in range(self.start, self.stop, 100):
      chunkStop = chunkStart + 100 if chunkStart + 100 < self.stop else self.stop
      
      chunkMatchDict = self.api.watcher.match.matchlist_by_account(
        region = self.api.region, 
        encrypted_account_id = self.accId, 
        queue = self.queueCodes, 
        begin_index = chunkStart, #Inclusive 
        end_index = chunkStop, #Exclusive
        champion = self.champions)

      matchlist.append(chunkMatchDict['matches'])
    print("Complete.")

    return matchlist

  def getSavedMatches(self, username):
    '''Return list of dictionaries containing match information from the given users locally saved 
    matches, or an empty list if none'''

    print("Loading locally saved matches... ", end='')
    try:
      with open(self.relativePath, 'r', encoding="utf-8") as saveFile:
        print("Complete. (File Loaded)")
        return list(json.load(saveFile))
      
    except json.JSONDecodeError as e:
      print(e)
      userInput = None
      while not (userInput == 'y' or 'n'):
        userInput = input("Would you like to overwrite the current faulty file? (y/n): ")
      if userInput == "y" or userInput == "yes":
        os.remove(self.filename)
        print("Complete. (Erroneous File Deleted)")
        return []
      else:
        raise
    except FileNotFoundError:
      print("Complete. (None Found)")
      return []

  def getNewMatchDetailsList(self, matchlist):
    print("Pulling match details for new matches... \n [", end='')
    savedMatches = self.getSavedMatches(username)
    newMatches = []
    for matchIndex in range(self.start, self.stop):
      curMatch = matchlist[matchIndex]['gameId']
      print(chr('254'), end='')
      # Check for previously saved match
      isNewMatch = True
      for savedMatch in savedMatches:
          if  curMatch == savedMatch['gameid']:
            isNewMatch = False
            break
      
      if isNewMatch:
        newMatches.append(self.api.watcher.match.by_id(self.region, curMatch))
    print("] Complete.")
    return newMatches

  def saveNewMatches(self, matchList):
    pass

  def update(self):
    newMatchList = self.pullMatchList(username, region=self.region, start=self.start, stop=self.stop, 
      champions=self.champions, queue=self.queue)
    newMatchDetailList = self.getNewMatchDetailsList(newMatchList)
    self.saveNewMatches(newMatchDetailList)