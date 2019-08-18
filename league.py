import pandas as pd
import math

import settings
import greedy_gm
import human_gm
import yahoo_gm
import subtractive_gm
import fanager
import operations



def main():
	#get players
	try:
		df = pd.read_csv(settings.CSV_FILE_NAME)
	except:
		import hockey_reference_scraper as hrs
		hrs.pull_all_historical_data(2018, 2019,settings.CSV_FILE_NAME[0:-4])
		df = pd.read_csv(settings.CSV_FILE_NAME)

	print_live = 0 # 1 = print while draft, 0 = print rosters at end

	# roster positions [C, LW, RW, D, G, Bonus]
	pos = [4,4,4,5,3,6]

	# number of rounds (# of players to be drafted)
	num_rounds = 5#sum(pos)

	# teams
	teams = [human_gm, yahoo_gm, subtractive_gm, greedy_gm]

	# simulate the draft
	draft = operations.draft(teams,df,num_rounds,pos,print_live)
	if print_live == 0: print(draft[['Player','Position','Team']])

	for i in range(len(teams)):
		
		score = 0
		#drafted_players = draft[draft.Team == teams[i].get_team_name()].reset_index(drop=True)
		drafted_players = draft[draft.ID == i].reset_index(drop=True)
		players = fanager.get_CPG(df).reset_index(drop=True)

		for p in range(len(drafted_players)):
			player_name = drafted_players.loc[p,"Player"]
			score = score + float(players.loc[players['Player']==player_name, 'CPG'])


		print(teams[i].get_team_name(), score)

if __name__ == "__main__":
	main()