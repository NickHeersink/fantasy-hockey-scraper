import pandas as pd
import math

import settings
import standard_gm
import fanager
import operations



def main():
	#get players
	df = pd.read_csv(settings.CSV_FILE_NAME)

	# number of rounds
	num_rounds = 5

	# array of team names
	team_names = ["Team A", "Team B"]
	# array of player selection functions
	team_draft = [standard_gm.make_draft_pick, standard_gm.make_draft_pick]

	# simulate the draft
	draft = operations.draft(df,num_rounds,team_names,team_draft)
	print draft

if __name__ == "__main__":
	main()