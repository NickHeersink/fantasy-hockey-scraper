import pandas as pd
import settings
import math
import pdb
from os import system, name

def draft(teams,player_list,num_rounds,positions,print_live=0):

	#TODO - add position limitations
	#	  - add protection against invalid picks (if pick is invalid, remove player from list and retry)

	team_names = [0]*len(teams) # empty array with same length as # of teams
	for n in range(len(team_names)):
		team_names[n] = teams[n].get_team_name() # set team names

	# dataframe of drafted players
	draft_list = pd.DataFrame(columns=["Player","Position","Team"])

	# r number of rounds in draft
	for r in range(0,num_rounds):
		# for t number of teams
		for t in range(0,len(teams)):
			# team makes a selection based on currenly available players
			player = teams[t].make_draft_pick(player_list,draft_list,positions,len(teams))
			position = player_list.loc[player_list["Player"] == player, 'Position'].values[0]

			# add new player to draft list	
			draft_list = draft_list.append({'Player': player, 'Position': position, 'Team': team_names[t]}, ignore_index=True)
			
			# drop player from remaining players
			player_list = player_list[player_list.Player != player]

			if print_live == 1:
				print(player, position, team_names[t])
				#system('cls')
				#print draft_list

	
	return draft_list

#================================= Main Function ================================================

def main():

	print("operations main() is empty")

if __name__ == "__main__":
	main()