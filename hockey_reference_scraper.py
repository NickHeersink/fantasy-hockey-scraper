import draft_rank
import requests
from bs4 import BeautifulSoup

# The keys are the HTML table elements BeautifulSoup records
# The values in the dictionary are the titles of the CSV and Pandas columns
category_dict = {
	"team_id": "Team",
	"pos": "Position",
	"games_played": "Games Played",
	"goals": "Goals",
	"assists": "Assists",
	"points": "Points",
	"pen_min": "Penalty Minutes",
	"blocks": "Blocks",
	"hits": "Hits",
	"wins_goalie": "Wins",
	"save_pct": "Save Percentage",
	"goals_against_avg": "Goals Against Average",
	"shutouts": "Shutouts"
}

# Goes through an individual player stats and adds their stats to the CSV if they are in the original list
def parse_individual_stats(df, row):
	cells = row.find_all('td')

	# Not sure why errors sometimes happen reading rows but we can skip to the next iteration
	try:
		name = cells[0].find(text=True)

		# Get the real Mitch Marner
		if name == "Mitch Marner":
			name = "Mitchell Marner"
	except:
		return

	# Check if the player is in the list of drafted players
	if df['Player'].str.contains(name).any():

		# Loop through each column and check if it's in the dictionary of stuff we should record
		for cell in cells:
			if cell['data-stat'] in category_dict.keys():
				df.loc[df.index.values[df.Player == name], category_dict[cell['data-stat']]] = cell.find(text=True)

# Gets the individual player stats from Hockey Reference
def get_player_stats(df, player_type):
	page_link = 'https://www.hockey-reference.com/leagues/NHL_2019_' + player_type + '.html'

	page_response = requests.get(page_link, timeout=5)

	# Make a fresh bowl of soup using BeautifulSoup. All page info contained in the 'soup' variable
	soup = BeautifulSoup(page_response.content, "html.parser")

	stats_table = soup.find('table', attrs={'class':'stats_table'})
	stats_table_body = stats_table.find('tbody')

	rows = stats_table_body.find_all('tr')
	for row in rows:
		parse_individual_stats(df, row)

def main():
	df = draft_rank.get_info()
	
	get_player_stats(df, 'skaters')
	get_player_stats(df, 'goalies')

	draft_rank.store_info(df)

if __name__ == "__main__":
	main()