import pandas as pd
import settings
import math
import pdb
import fanager

def make_draft_pick(players):
	#players - remaining players
	#picks   - players already picked by this gm

	players = eval_skaters(players)
	# selects top rated player to draft
	return players.loc[0,"Player"]

def eval_skaters(df):
	df = fanager.get_CPG(df) # add CPG to dataframe
	df = df[df.Position != 'G'] # get rid of goalies
	df = df.sort_values(['CPG'], ascending=False) # sort by highest CPG
	#df = df[["Player","CPG"]] # get rid of unnecessary columns
	df = df.reset_index(drop=True) # reindex
	return df

def eval_goalies(df):
	df = fanager.get_CPG(df) # add CPG to dataframe
	df = df[df.Position == 'G'] # get rid of non-goalies
	df = df.sort_values(['CPG'], ascending=False) # soft by highest CPG
	#df = df[["Player","CPG"]] # get rid of unnecessary columns
	df = df.reset_index(drop=True) # reindex
	return df

def main():
	print "Hello"

if __name__ == "__main__":
	main()