import pandas as pd
import settings
import math
import pdb
import fanager

pos_dict = {
	"C": 0,
	"LW": 1,
	"RW": 2,
	"D": 3,
	"G": 4,
	"X": 5
}

def get_team_name():
	return "Greedy AI"

def make_draft_pick(players,drafts,ref_pos):
	#players - remaining players
	#picks   - players already picked in draft
	#pos 	 - roster positions
	
	# have to do this nonsense b/c python can't pass by value and apparently deepcopy doesn't actually unlink things 
	pos = [None]*len(ref_pos)
	for i in range(len(ref_pos)):
		pos[i] = ref_pos[i]

	pos = update_pos(drafts,pos) # update positions remaining
	
	players = eval_players(players)
	# find top ranked player that fits in remaining positions
	for i in range(len(players)):
		if (pos[pos_dict[players.loc[i,"Position"]]] > 0) or (pos[5] > 0): 
			return players.loc[0,"Player"]
	
	return players.loc[0,"Player"]

def eval_players(df):
	df = fanager.get_CPG(df) # add CPG to dataframe
	df = df.sort_values(['CPG'], ascending=False) # sort by highest CPG
	#df = df[["Player","CPG"]] # get rid of unnecessary columns
	df = df.reset_index(drop=True) # reindex
	return df

def update_pos(drafts,pos):
	
	drafts = drafts[drafts.Team == get_team_name()]
	drafts = drafts.reset_index(drop=True) # reindex
	
	for i in range(len(drafts)):
		p = pos_dict[drafts.loc[i,"Position"]]
		if (pos[p] > 0): pos[p] = pos[p]-1
		else: pos[5] = pos[5]-1
	
	return pos

def main():
	print "Hello"

if __name__ == "__main__":
	main()