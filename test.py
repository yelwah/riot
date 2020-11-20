from os import terminal_size, truncate
from riotapi.riot_api import Api, Player, getChampDict
from operator import itemgetter

apiKey = Api("RGAPI-aba610f6-d992-4039-a03d-b460f26719bf")
player: Player = Player(apiKey, "Yelwah")
print(player.accId)
player.matchData.updateMatchData()

# BLUE_TEAM, RED_TEAM = 100, 200
# for match in player.matchData.matchDetailData:
#   # Get my participant id from my summoner name
#   myParticipantId = -1
#   for participant in match['participantIdentities']:
#     if participant['player']['summonerName'].lower() == player.name.lower():
#       myParticipantId = int(participant['participantId'])
#       break
#   assert(myParticipantId >= 1 and myParticipantId <= 10)

#   # Get teams & winner relative to me
#   myTeam = None
#   enemyTeam = None
#   myWin = None
#   myTeam = int(match['participants'][myParticipantId-1]['teamId'])
#   myWin = match['participants'][myParticipantId-1]['stats']['win']
 
#   assert(myTeam == BLUE_TEAM or myTeam == RED_TEAM)
#   if myTeam == BLUE_TEAM:
#     enemyTeam = RED_TEAM
#   else:
#     enemyTeam = BLUE_TEAM
#   if myWin:
#     myWin = 1
#   else:
#     myWin = 0
#   assert(myWin == 0 or myWin == 1)

#   # Add champion matchup data to me for each enemy player
#   for participant in match['participants']:
#     if int(participant["teamId"]) == enemyTeam:
#       player.addMatchupResult(int(participant['championId']), myWin)

# versusWinrates = {}
# for key, champion in player.matchups.items():
#   versusWinrates[champion.name] = [champion.totalMatches, round(champion.getWinningPct(), 2), champion.wins - champion.getLosses()]
#   # if champion.getWinningPct() == -1:
#   #   print(champion.name + " - Games: " + str(champion.totalMatches))
#   # else:
#   #   print(champion.name + " - Games: " + str(champion.totalMatches) + ", Win Pct: " + str(round(champion.getWinningPct(), 2)) + "%")
# sortedMatchupDict = sorted(versusWinrates.items(), key=lambda item: item[1][2])
# for x in sortedMatchupDict:
#   print(x[0] + ":",  "Net Wins:", str(x[1][2]) + ",", "Winning %:", str(x[1][1]) + ",", "Total Games:", str(x[1][0]))