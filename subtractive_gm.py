import pandas as pd
import settings
import math
import pdb
import fanager
import copy

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

def make_draft_pick(players,drafts,ref_pos):
	#players - remaining players
	#picks   - players already picked in draft
	#ref_pos - roster positions
	
	# have to do this nonsense b/c python can't pass by value and apparently deepcopy doesn't actually unlink things 
	pos = [None]*len(ref_pos)
	for i in range(len(ref_pos)):
		pos[i] = ref_pos[i]
	
	pos = update_pos(drafts,pos) # update positions remaining
	
	players = eval_players(players) # add eval column
	my_drafts = drafts[drafts == get_team_name()] # remove all other draft picks

	top_players = pd.DataFrame(columns=['Player','Position','CPG','dCPG'])
	top_players = top_players.fillna(0)

	# for all position
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

			# if there are available players in that position
			if len(players_in_pos) > 0: 
				players_in_pos = players_in_pos.sort_values(['CPG'], ascending=False)
				best_player = players_in_pos.iloc[[0]] # best player in that position
				top_players = top_players.append(best_player[['Player','Position','CPG']], sort=True)

				# dCPG = CPG of best player - CPG of nth best player (where n = # of slots open + 1)
				top_players.iloc[-1, top_players.columns.get_loc('dCPG')] = float(top_players.iloc[len(top_players)-1].CPG - players_in_pos.iloc[pos[pos_dict[p]]].CPG)	


	top_players = top_players.sort_values(['dCPG'], ascending=False) # sort by highest CPG
	top_players = top_players.reset_index(drop=True)
	return top_players.loc[0,'Player']
		
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