from riotapi import matchPuller, utilities as apiUtil
from analysis.matchup import Matchup
from analysis import utilities as anUtil


username = "TTeBroc"
api = apiUtil.Api()
matchup = Matchup(api, username)
matchPuller.MatchPuller.pullAndSave(api, username, start=140, stop=150)
# matchPuller.pullAndSaveNew(api, username)
print(len(matchup.matchData))

versusStats = []
for key, champion in matchup.matchupDict.items():
  versusStats.append([champion.name, champion.totalMatches, round(champion.getWinningPct(), 2), champion.wins - champion.getLosses()])

anUtil.outputToExcel(username, headings = ['Champion', 'Total Games', 'Winrate', 'Net Wins'], rowContent = versusStats)