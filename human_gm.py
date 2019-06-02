import pandas as pd
import settings
import math
import pdb
import fanager

def make_draft_pick(players):
	#players - remaining players
	#picks   - players already picked by this gm

	players = players.reset_index(drop=True) # reindex
	# selects player humans drafted first
	return players.loc[0,"Player"]

def main():
	print "Hello"

if __name__ == "__main__":
	main()