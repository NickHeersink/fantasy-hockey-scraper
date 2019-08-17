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
	df = pd.read_csv(settings.CSV_FILE_NAME)

	print_live = 0

	# roster positions [C, LW, RW, D, G, Bonus]
	pos = [4,4,4,5,3,6]

	# number of rounds (# of players to be drafted)
	num_rounds = sum(pos)

	# teams
	teams = [human_gm, yahoo_gm, subtractive_gm, greedy_gm]

	# simulate the draft
	draft = operations.draft(teams,df,num_rounds,pos,print_live)
	if print_live == 0: print(draft)

	for i in range(len(teams)):
		
		score = 0
		drafted_players = draft[draft.Team == teams[i].get_team_name()].reset_index(drop=True)
		#drafted_players = drafted_players.reset_index(drop=True)

		for p in range(len(drafted_players)):
			player_name = drafted_players.loc[p,"Player"]
			player = df[df.Player == player_name]
			player = fanager.get_CPG(player).reset_index(drop=True) # get player details from main dataframe
			score = score + player.loc[0,"CPG"]


		print(teams[i].get_team_name(), score)

if __name__ == "__main__":
	main()