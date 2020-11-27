from riotapi.utilities import Api, getAccID
from requests.exceptions import HTTPError
import json, time, os
from typing import Set

class MatchPuller():
  def pullListAll(api: Api, username, start, stop):
    '''Return a List of Dictionaries with basic match data for a sequence of matches with specific
    account name'''
    if stop == None:
      matchlist = api.watcher.match.matchlist_by_account(
        region = api.region, 
        encrypted_account_id = getAccID(api, username), 
        begin_index = 99999, #Inclusive 
        end_index = 100000) #Exclusive
      stop = matchlist['endIndex']
    matchlist: Set[dict] = []
    for chunkStart in range(start, stop, 100):
      chunkStop = chunkStart + 100 if chunkStart + 100 < stop else stop
      
      chunkMatchDict = api.watcher.match.matchlist_by_account(
        region = api.region, 
        encrypted_account_id = getAccID(api, username), 
        begin_index = chunkStart, #Inclusive 
        end_index = chunkStop) #Exclusive
      matchlist = matchlist + (chunkMatchDict['matches'])
    return matchlist

  def pullDetailsDelta(api, username, matchlist):
    '''Return a list of match details given a list of matches. Match details that have already been
    saved will not be included in the returned list.
    '''
    # Load all the locally saved match details to compare against
    savedMatches = MatchPuller.load(username)

    # Iteratively pull new match details and append them to the list that will be returned
    newMatches = []
    print("Requesting match details...", flush=True)
    count = 0
    for match in matchlist:
      
      # Check for previously saved match
      isNewMatch = True
      for savedMatch in savedMatches:
        if match['gameId'] == savedMatch['gameId']:
          isNewMatch = False
          break
      
      # Pulls new match's details and repeats if unsuccessful
      if isNewMatch:
        done = False
        while not done:
          try:
            newMatches.append(api.watcher.match.by_id(api.region, match['gameId']))
            done = True
          except HTTPError as e:
            time.sleep(0.1)
      count += 1
      print(".", end = '', flush = True)
      if count % 10 == 0:
        print(" ", end = '', flush = True)
        if count % 100 == 0:
          print()
          count = 1
    print()
    return newMatches

  def pullDetailsAll(api, matchlist):
    '''Return a list of match details for the given list of matches, does not compare against 
    locally saved matches
    '''
    newMatches = []
    print("Requesting match details...", flush=True)
    count = 0
    for match in matchlist:
      # Check for previously saved match
      done = False
      while not done:
        try:
          newMatches.append(api.watcher.match.by_id(api.region, match['gameId']))
          done = True
        except HTTPError as e:
          time.sleep(0.1)
      count += 1
      print(".", end = '', flush = True)
      if count % 10 == 0:
        print(" ", end = '', flush = True)
        if count % 100 == 0:
          print()
          count = 1
    print()
    return MatchPuller.sortDetailList(newMatches)

  def getSavePath(username): return 'match_data/' + username + ".json"

  def load(username):
    '''Return list of dictionaries containing match information from the given users locally saved 
    matches, or an empty list if none
    '''

    print("Loading locally saved matches... ", end='', flush=True)
    try:
      with open(MatchPuller.getSavePath(username), 'r', encoding="utf-8") as saveFile:
        print("Complete. (File Loaded)", flush=True)
        return list(json.load(saveFile))
      
    except json.JSONDecodeError as e:
      print(e)
      userInput = None
      while not (userInput == 'y' or 'n'):
        userInput = input("Would you like to overwrite the current faulty file? (y/n): ")
      if userInput == "y" or userInput == "yes":
        os.remove(MatchPuller.getSavePath(username))
        print("Complete. (Erroneous File Deleted)", flush=True)
        return []
      else:
        raise
    except FileNotFoundError:
      print("Complete. (None Found)", flush=True)
      return []

  def save(username, matchDetailList):
    with open(MatchPuller.getSavePath(username), 'w', encoding="utf-8") as outfile:
      json.dump(matchDetailList, outfile)   

  def pullAndSave(api: Api, username: str, start: int, stop: int = None):
    '''Pull a given range of matches for a given user and save them locally
    '''
    newMatchList = MatchPuller.pullListAll(api, username, start, stop)
    newMatchDetailList = MatchPuller.pullDetailsDelta(api, username, newMatchList)
    MatchPuller.save(username, MatchPuller.sortDetailList(MatchPuller.load(username) + newMatchDetailList))
    print("Pulled matches from " + str(start) + ' to ' + str(stop) + ". (" + str(stop - start) + " matches)")
  
  def pullListNew(api: Api, username: str):
    '''Pull matches only more recent than the most recent match saved locally'''
    start = 0
    savedMatches = MatchPuller.load(username)
    if savedMatches == []:
      return []
    sortedMatches = MatchPuller.sortDetailList(savedMatches)
    mostRecentSavedMatch = sortedMatches[-1]

    numNewMatches = 0
    foundMostRecentLocalMatch = False
    while not foundMostRecentLocalMatch:
      stop = start + 100
      matchlist = MatchPuller.pullListAll(api, username, start, stop)
      for match in matchlist:
        if mostRecentSavedMatch['gameId'] == match['gameId']:
          foundMostRecentLocalMatch = True
          break
        else:
          numNewMatches += 1
      start += 100
    print("numNewMatches = " + str(numNewMatches))
      
    return MatchPuller.pullListAll(api, username, 0, numNewMatches)
  
  def pullAndSaveNew(api: Api, username: str):
    newMatchList = MatchPuller.pullListNew(api, username)
    newMatchDetailList = MatchPuller.pullDetailsAll(api, newMatchList)
    MatchPuller.save(username, (MatchPuller.sortDetailList(MatchPuller.load(username) + newMatchDetailList)))
    print("Pulled " + str(len(newMatchList)) + " new matches.")
 
  def sortDetailList(matchDetailList, sortKey='gameId'): return sorted(matchDetailList, key = lambda x: x[sortKey])