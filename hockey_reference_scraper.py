import yahoo_scraper
import settings

import pandas
import requests
#import unidecode
import pdb

from bs4 import BeautifulSoup

# The keys are the HTML table elements BeautifulSoup records
# The values in the dictionary are the titles of the CSV and Pandas columns
category_dict = {
	"team_id": "Team",
	"pos": "Position",
	"games_played": "Games Played",
	"games_goalie": "Games Played",
	"goals": "Goals",
	"assists": "Assists",
	"points": "Points",
	"pen_min": "Penalty Minutes",
	"blocks": "Blocks",
	"hits": "Hits",
	"wins_goalie": "Wins",
	"goals_gw": "Game Winning Goals",
	"goals_sh": "Shorthanded Goals",
	"assists_sh": "Shorthanded Assists",
	"save_pct": "Save Percentage",
	"goals_against_avg": "Goals Against Average",
	"shutouts": "Shutouts"
}

fake_bois = {
	"Mitch Marner": "Mitchell Marner",
	"Alex Steen": "Alexander Steen",
	"Jake Debrusk": "Jake DeBrusk",
	"Jon Marchessault": "Jonathan Marchessault",
	"Mathew Dumba": "Matt Dumba"
}


# Search through the list of mismatched names and return the way it is stored in Yahoo
def check_fake_bois(name):
	if name in fake_bois.keys():
		name = fake_bois[name]

	return name


# Goes through an individual player stats and adds their stats to the CSV if they are in the original list
def parse_individual_stats(df, row, pull_all_players):
	cells = row.find_all('td')

	# Not sure why errors sometimes happen reading rows but we can skip to the next iteration
	try:
		name = cells[0].find(text=True)

		name = check_fake_bois(name)
	except:
		return

	# Check if the player is in the list of drafted players
	if not pull_all_players and df['Player'].str.contains(name).any():
		# Loop through each column and check if it's in the dictionary of stuff we should record
		for cell in cells:
			if cell['data-stat'] in category_dict.keys():
				df.loc[df.index.values[df.Player == name], category_dict[cell['data-stat']]] = cell.find(text=True)

	elif pull_all_players:
		# Encode to ASCII to prevent player name errors
		df.loc[len(df), 'Player'] = name
		print(name)

		for cell in cells:
			if cell['data-stat'] in category_dict.keys():
				df.loc[len(df) - 1, category_dict[cell['data-stat']]] = cell.find(text=True)


def fill_in_blank_cells(df):
	for row_index, player in df.iterrows():
		# Add goalie positions to CSV. Assumes missing positions are for goalies
		if pandas.isnull(player.Position):
			df.at[row_index, 'Position'] = 'G'

		# Add zeroes to any blank cells
		for col_index, category in enumerate(player):
			if pandas.isnull(df.iloc[row_index,col_index]):
				df.iat[row_index, col_index] = 0

	return df


def add_shorthanded_points(df):
	# Convert columns to integers
	df[["Shorthanded Goals", "Shorthanded Assists"]] = df[["Shorthanded Goals", "Shorthanded Assists"]].apply(pandas.to_numeric)

	df['Shorthanded Points'] = df['Shorthanded Goals'] + df['Shorthanded Assists']

	return df


# Gets the individual player stats from Hockey Reference
def get_player_stats(df, player_type, year, pull_all_players):
	page_link = 'https://www.hockey-reference.com/leagues/NHL_' + str(year) + '_' + player_type + '.html'

	page_response = requests.get(page_link, timeout=5)

	# Make a fresh bowl of soup using BeautifulSoup. All page info contained in the 'soup' variable
	soup = BeautifulSoup(page_response.content, "html.parser")

	stats_table = soup.find('table', attrs={'class':'stats_table'})
	stats_table_body = stats_table.find('tbody')

	rows = stats_table_body.find_all('tr')
	for row in rows:
		parse_individual_stats(df, row, pull_all_players)


# Look through the dataframe and removes all non 'TOT' duplicates
def eliminate_duplicates(df):
	# Loop through backwards to delete the proper index
	for i, player in df[::-1].iterrows():
		if len(df[df.Player == player.Player]) > 1:
			if player.Team != "TOT":
				df.drop(df.index[i], inplace=True)

	return df.reset_index(drop=True)


# Put in any functions to clean up the dataframe
def clean_up_dataframe(df):
	df = eliminate_duplicates(df)
	df = fill_in_blank_cells(df)
	df = add_shorthanded_points(df)

	return df


def pull_league_data_only():
	df = yahoo_scraper.get_info()
	
	get_player_stats(df, 'skaters', 2019, False)
	get_player_stats(df, 'goalies', 2019, False)

	clean_up_dataframe(df)

	yahoo_scraper.store_info(df, settings.CSV_FILE_NAME)


def pull_all_historical_data(start_year, end_year):
	for current_year in range(start_year, end_year):
		print('Pulling data for ' + str(current_year))

		df = pandas.DataFrame()

		get_player_stats(df, 'skaters', current_year, True)
		get_player_stats(df, 'goalies', current_year, True)

		df = clean_up_dataframe(df)

		yahoo_scraper.store_info(df, 'all_player_data_' + str(current_year) + '.csv')


def main():
	pull_all_historical_data(2018, 2019)


if __name__ == "__main__":
	main()