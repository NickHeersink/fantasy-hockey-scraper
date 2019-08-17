import pandas as pd
import settings
import math
import pdb
import fanager
import copy
import numpy

# TODO - include more players in dCPG calc by add a waiting to the dCPG calc of players based on the likelyhood of being drafted
# 		 maybe add a multiplier on to the dCPG calc based on number of rounds?
#		 i.e top x number of player (where x = number of teams) get a dCPG multiplier of 1 but in subsequent rounds it decreases?
#		 might have to reword the whole equation to be a weighted some of CPGs of potential draftees? idk

pos_dict = {
	"C": 0,
	"LW": 1,
	"RW": 2,
	"D": 3,
	"G": 4,
	"X": 5
}

def get_team_name():
	return "Defensive AI"


def make_draft_pick(players,drafts,ref_pos,num_teams):
	#players - remaining players
	#picks   - players already picked in draft
	#ref_pos - roster position

	# have to do this nonsense b/c python can't pass by value and apparently deepcopy doesn't actually unlink things 
	pos = [None]*len(ref_pos)
	for i in range(len(ref_pos)):
		pos[i] = ref_pos[i]
	
	pos = update_pos(drafts,pos) # update positions remaining
	
	players = eval_players(players) # add eval column
	# players with high likelyhood to be drafted in next round
	exp_players_drafted = players.sort_values(['Rank'], ascending=True).head(num_teams*2)

	top_players = pd.DataFrame(columns=['Player','Position','CPG','dCPG']) # players that might be drafted next round
	
	# for all positions on team
	for p in pos_dict:
		# if have space for a player in that position
		if pos[pos_dict[p]] > 0: 
			# get all players in that position
			players_in_pos = players.loc[players.Position == p]

			# if position is wild card
			if p == 'X':
				# get list of players that aren't in the remaining position slots
				# eg. if there are 2 center slots still open, drop the top 2 centers
				for x in pos_dict:
					players_in_pos = players_in_pos.append(players.loc[players.Position == x].iloc[pos[pos_dict[x]]:])


			num_exp_player_in_pos = len(exp_players_drafted.loc[exp_players_drafted['Position'] == p])
					
			# if there are available players in that position and players expected to be drafted in that position
			if (len(players_in_pos) > 0): 
				players_in_pos = players_in_pos.sort_values(['CPG'], ascending=False)
				best_player = players_in_pos.iloc[[0]] # best player in that position
				top_players = top_players.append(best_player[['Player','Position','CPG']], sort=True)

				# dCPG = CPG of best player - CPG of nth best player, where n = # of slots open + number of players in that position to be expected to be drafted
				n = pos[pos_dict[p]] + num_exp_player_in_pos
				top_players.iloc[-1, top_players.columns.get_loc('dCPG')] = float(top_players.iloc[len(top_players)-1].CPG - players_in_pos.iloc[n].CPG)	
			

	top_players = top_players.fillna(0)

	top_players = top_players.sort_values(['dCPG'], ascending=False) # sort by highest CPG
	top_players = top_players.reset_index(drop=True)


	# return player with highest dCPG, or if all zero return player with highest CPG
	if top_players.loc[0,'Player'] > 0: return top_players.loc[0,'Player']
	else: return top_players.loc[top_players.index(top_players.CPG), 'Player']
		
def eval_players(df):
	df = fanager.get_CPG(df) # add CPG to dataframe
	df = df.sort_values(['CPG'], ascending=False) # sort by highest CPG
	#df = df[["Player","CPG"]] # get rid of unnecessary columns
	df = df.reset_index(drop=True) # reindex
	return df

def update_pos(drafts,pos):
	
	drafts = drafts[drafts.Team == get_team_name()] # get draft picks made by this team
	drafts = drafts.reset_index(drop=True) # reindex
	
	for i in range(len(drafts)):
		p = pos_dict[drafts.loc[i,"Position"]]
		if pos[p] > 0: pos[p] = pos[p]-1
		else: pos[5] = pos[5]-1
	
	return pos

def main():
	players = pd.read_csv(settings.CSV_FILE_NAME)
	drafts = pd.DataFrame(columns=players.columns)
	pos = [4,4,4,5,3,6]

	make_draft_pick(players,drafts,pos)

if __name__ == "__main__":
	main()