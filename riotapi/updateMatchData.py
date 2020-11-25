from riotapi.utilities import getSavedMatches, Api
from requests.exceptions import HTTPError
from riotwatcher import LolWatcher, ApiError
from riotapi import utilities as riotUtil
import json, os, time
from typing import Set

class MatchUpdater():
  def pullMatchList(api, username, start, stop):
    '''Return a List of Dictionaries with basic match data for a sequence of matches with specific
    account name'''
    if stop == None:
      matchlist =  api.watcher.match.matchlist_by_account(
        region = api.region, 
        encrypted_account_id = riotUtil.getAccID(api, username), 
        begin_index = 99999, #Inclusive 
        end_index = 100000) #Exclusive
      stop = matchlist['endIndex']
    matchlist: Set[dict] = []
    for chunkStart in range(start, stop, 100):
      chunkStop = chunkStart + 100 if chunkStart + 100 < stop else stop
      
      chunkMatchDict = api.watcher.match.matchlist_by_account(
        region = api.region, 
        encrypted_account_id = riotUtil.getAccID(api, username), 
        begin_index = chunkStart, #Inclusive 
        end_index = chunkStop) #Exclusive
      matchlist = matchlist + (chunkMatchDict['matches'])
    return matchlist

  def getUnsavedMatchDetails(api, username, matchlist):
    '''Return a list of match details given a list of matches. Match details that have already been
    saved will not be included in the returned list.
    '''
    # Load all the locally saved match details to compare against
    savedMatches = riotUtil.getSavedMatches(username)

    # Iteratively pull new match details and append them to the list that will be returned
    newMatches = []
    print("Requesting match details", end="", flush=True)
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
            print(e.args)
            print(e.errno)
            time.sleep(0.5)

      print(".", end = '', flush = True)
    print()
    return newMatches

  def getMatchDetails(api, matchlist):
    '''Return a list of match details for the given list of matches, does not compare against 
    locally saved matches
    '''
    newMatches = []
    print("Requesting match details", end="", flush=True)
    for match in matchlist:
      # Check for previously saved match
      done = False
      while not done:
        try:
          newMatches.append(api.watcher.match.by_id(api.region, match['gameId']))
          done = True
        except HTTPError as e:
          print(e.args)
          print(e.errno)
          time.sleep(0.5)
      print(".", end = '', flush = True)
      print()
    return MatchUpdater.sortMatches(newMatches)

  def saveMatches(username, matchDetailList, flag='w'):
    with open(riotUtil.getMatchDataPath(username), flag, encoding="utf-8") as outfile:
      json.dump(matchDetailList, outfile)   

  def pullMatchSet(api: Api, username: str, start: int, stop: int = None):
    '''Pull a given range of matches for a given user and save them locally
    '''
    newMatchList = MatchUpdater.pullMatchList(api, username, start, stop)
    newMatchDetailList = MatchUpdater.getUnsavedMatchDetails(api, username, newMatchList)
    MatchUpdater.saveMatches(username, newMatchDetailList)
    print("Pulled matches from " + str(start) + ' to ' + str(stop) + ". (" + str(stop - start) + " matches)")
  
  def pullNewMatchList(api: Api, username: str):
    '''Pull matches only more recent than the most recent match saved locally'''
    start = 0
    savedMatches = riotUtil.getSavedMatches(username)
    sortedMatches = MatchUpdater.sortMatches(savedMatches)
    mostRecentSavedMatch = sortedMatches[-1]

    numNewMatches = 0
    foundMostRecentLocalMatch = False
    while not foundMostRecentLocalMatch:
      stop = start + 100
      matchlist = MatchUpdater.pullMatchList(api, username, start, stop)
      for match in matchlist:
        if mostRecentSavedMatch['gameId'] == match['gameId']:
          foundMostRecentLocalMatch = True
          break
        else:
          numNewMatches += 1
      start += 100
    print("numNewMatches = " + str(numNewMatches))
      
    return MatchUpdater.pullMatchList(api, username, 0, numNewMatches)
  
  def pullNewMatches(api: Api, username: str):
    newMatchList = MatchUpdater.pullNewMatchList(api, username)
    newMatchDetailList = MatchUpdater.getMatchDetails(api, username, newMatchList)
    MatchUpdater.saveMatches(username, newMatchDetailList, 'a')
    print("Pulled " + str(len(newMatchList)) + " new matches.")
 
  def sortMatches(matchDetailList, sortKey='gameId'):
    return sorted(matchDetailList, key = lambda x: x[sortKey])
