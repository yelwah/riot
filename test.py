from riotapi.matchup import Matchup
import riotapi.utilities as util

from typing import List, Any

username = "Yelwah"
matchup = Matchup(util.Api(), username)

totalwins = 0
totallosses = 0
for match in matchup.matchData:
  # Get my participant id from my summoner name
  myParticipantId = -1
  for participant in match['participantIdentities']:
    if participant['player']['summonerName'].lower() == username.lower():
      myParticipantId = int(participant['participantId'])
      break
  assert(myParticipantId >= 1 and myParticipantId <= 10)

  # Get teams & winner relative to me
  myTeam = None
  enemyTeam = None
  myWin = None
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
      matchup.addMatchupResult(int(participant['championId']), myWin)

versusStats = []
for key, champion in matchup.matchupDict.items():
  versusStats.append([champion.name, champion.totalMatches, round(champion.getWinningPct(), 2), champion.wins - champion.getLosses()])

util.outputToExcel(username, headings = ['Champion', 'Total Games', 'Winrate', 'Net Wins'], rowContent = versusStats)