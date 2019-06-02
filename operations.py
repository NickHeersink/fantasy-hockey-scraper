import pandas as pd
import settings
import math
import pdb

def draft(player_list,num_rounds,team_names,team_draft):

	# dataframe of drafted players and their stats
	draft_list = pd.DataFrame(columns=['Player','Team'])

	# r number of rounds in draft
	for r in range(0,num_rounds):
		# for t number of teams
		for t in range(0,len(team_names)):
			
			# team makes a selection based on currenly available players
			player = team_draft[t](player_list)

			#add new player to draft list	
			draft_list = draft_list.append({'Player': player, 'Team': team_names[t]}, ignore_index=True)
			#drop player from remaining players
			player_list = player_list[player_list.Player != player]
			

	
	return draft_list

#================================= Main Function ================================================

def main():

	print "operations main() is empty"

if __name__ == "__main__":
	main()