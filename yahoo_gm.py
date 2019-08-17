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
	return "Yahoo"

def make_draft_pick(players,drafts,pos,num_teams):
	#players - remaining players
	#picks   - players already picked by this gm

	# selects player humans drafted first
	players = players.sort_values(['Rank'], ascending=True) # sort by yahoo ranking
	players = players.reset_index(drop=True) # reindex

	# find top ranked player that fits in remaining positions
	for i in range(len(players)):
		if (pos[pos_dict[players.loc[i,"Position"]]] > 0) or (pos[5] > 0): 
			return players.loc[0,"Player"]

	return players.loc[0,"Player"]

def update_pos(drafts,pos):
	
	drafts = drafts[drafts.Team == get_team_name()]
	drafts = drafts.reset_index(drop=True) # reindex
	
	for i in range(len(drafts)):
		p = pos_dict[drafts.loc[i,"Position"]]
		if (pos[p] > 0): pos[p] = pos[p]-1
		else: pos[5] = pos[5]-1
	
	return pos

def main():
	print("Hello")

if __name__ == "__main__":
	main()