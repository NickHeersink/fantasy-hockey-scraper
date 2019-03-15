import time
import pdb

import requests
from bs4 import BeautifulSoup

import pandas
import matplotlib.pyplot as plt

from selenium import webdriver

import settings
import stats

# Connect to Yahoo Fantasy
# Pass in the URL you'd like to go to immediately upon logging in
def login(driver, url):
	driver.get(url)

	username = driver.find_element_by_name('username')
	username.send_keys(settings.YAHOO_USERNAME)
	username.send_keys(u'\ue007')

	time.sleep(10)

	password = driver.find_element_by_name('password')
	password.send_keys(settings.YAHOO_PASSWORD)
	password.send_keys(u'\ue007')

# Get draft results
def get_draft_results(driver, df):
	players_web_elems = driver.find_elements_by_class_name('name')
	df['Player'] = [player.text for player in players_web_elems]

# Gets draft order (can be done offline knowing the order repeats)
def get_draft_order(df):
	draft_order = settings.DRAFT_ORDER
	draft_order = draft_order + list(reversed(draft_order))

	df['Drafter'] = draft_order * 13

# Get the player rankings from the player page
def get_player_information(driver, df):
	driver.get(settings.YAHOO_RANK_URL)

	search_box = driver.find_element_by_id('playersearchtext')

	for index, player in df.iterrows():
		print player.Player

		search_box.clear()
		search_box.send_keys(player.Player)
		search_box.send_keys(u'\ue007') # Press enter - TODO replace with clicking 'Search' button

		time.sleep(5)

		table = driver.find_element_by_class_name('players-table')
		rows = table.find_elements_by_tag_name('tr')

		columns = rows[2].find_elements_by_tag_name('td')

		df.loc[index, 'Rank'] = columns[6].text
		#df.loc[index, 'Team'] = columns[1].text.split(' ')[-3]
		#df.loc[index, 'Position'] = columns[1].text.split(' ')[-1]

		print('Ranking is: ' + df.loc[index, 'Rank'])

# Returns the real Sebastian Aho information
def get_the_real_aho(driver, df):
	search_box = driver.find_element_by_id('playersearchtext')

	search_box.clear()
	search_box.send_keys('Sebastian Aho')
	search_box.send_keys(u'\ue007') # Press enter - TODO replace with clicking 'Search' button

	time.sleep(5)

	table = driver.find_element_by_class_name('players-table')
	rows = table.find_elements_by_tag_name('tr')

	# The real Sebastian Aho can be found in column 6, row 3!!!!!!!
	columns = rows[3].find_elements_by_tag_name('td')
	df.loc[df.index.values[df.Player == 'Sebastian Aho'], 'Rank'] = columns[6].text
	#df.loc[df.index.values[df.Player == 'Sebastian Aho'], 'Team'] = columns[1].text.split(' ')[-3]
	#df.loc[df.index.values[df.Player == 'Sebastian Aho'], 'Position'] = columns[1].text.split(' ')[-1]

# Store info in .csv file using Pandas
def store_info(df):
	df.to_csv(settings.CSV_FILE_NAME)

# Writes the info in the .csv file to a Pandas dataframe
def get_info():
	return pandas.read_csv(settings.CSV_FILE_NAME, index_col=0)

def get_player_lists_by_person(df, person):
	return df.Player[df.Drafter == person]

def get_player_ranks_by_person(df, person):
	return df.Rank[df.Drafter == person]

def get_draft_spots_by_person(df, person):
	return df.index.values[df.Drafter == person]

# Get the residuals and add a column to the Pandas dataframe
def calculate_residuals(df, b, m):
	min_factor = b
	max_factor = m * len(df) + b

	residuals = []

	# Scale the residuals so that the earlier picks are weighted more heavily than the later ones
	for index, player in df.iterrows():
		residual = player.Expected - player.Rank

		scale_factor = min_factor / float(max_factor)
		scale_factor = 1 - index / float(len(df)) * scale_factor

		residuals.append(round(residual * scale_factor, 2))

	df['Residual'] = residuals

# Adds data labels for the n-best and n-worst players per drafter
def add_large_residuals(df, ax):
	worst_players = df.nsmallest(settings.NUM_RESIDUALS, 'Residual')
	best_players = df.nlargest(settings.NUM_RESIDUALS, 'Residual')

	for player in best_players.itertuples():
		ax.annotate(player.Player, xy=(player.Index, player.Rank), textcoords = 'data')

	for player in worst_players.itertuples():
		ax.annotate(player.Player, xy=(player.Index, player.Rank), textcoords = 'data')

# Filter the dataframe based on the drafter, teams, and/or position
# If these lists are empty, it will return all
def filter_df(df, search_drafters, search_teams, search_positions):
	filtered_df = pandas.DataFrame(columns=['Player','Rank','Residual','Team','Position'])

	if search_drafters:
		for person in search_drafters:
			filtered_df = filtered_df.append(df[df.Drafter == person])
	else:
		filtered_df = df

	# TODO - filter for teams and positions

	return filtered_df

# Plot the results
def plot_draft_results(df, search_drafters=[], search_teams=[], search_positions=[]):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	b, m = stats.get_line_of_best_fit_params(df.index.values, df.Rank)

	# Add the expected ranking to the dataframe
	df['Expected'] = [m*x + b for x in df.index.values]
	
	calculate_residuals(df, b, m)

	# Filter the data frame down to the search criteria
	filtered_df = filter_df(df, search_drafters, search_teams, search_positions)

	for person in settings.DRAFT_ORDER:
		personal_players = get_player_lists_by_person(filtered_df, person)
		personal_ranks = get_player_ranks_by_person(filtered_df, person)
		personal_draft = get_draft_spots_by_person(filtered_df, person)

		# Only add points if there are players for that drafter
		if not filtered_df[filtered_df.Drafter == person].empty:
			average_residual = sum([residual for residual in filtered_df.Residual[filtered_df.Drafter == person]]) / len(filtered_df[filtered_df.Drafter == person])
			ax.scatter(personal_draft, personal_ranks, label=person + " " + str(round(average_residual, 2)))

	r_squared = stats.calculate_coeff_determination(df.index.values, df.Rank, df.Expected)

	plt.plot(filtered_df.index.values, filtered_df.Expected)

	plt.legend(loc='upper left')
	plt.xlabel('Drafted Position')
	plt.ylabel('Actual Ranking')

	add_large_residuals(filtered_df, ax)

	plt.show()

# Clean up the Chrome webdriver
def end_connection(driver):
	driver.close()

# Call this function from main to produce a comparison for how everyone has drafted
def compare_drafter_rankings():
	print('Welcome to the Non-Competitive Action League')

	if settings.NEED_NEW_DATA:
		driver = webdriver.Chrome()
		driver.set_page_load_timeout(60)
		login(driver, settings.YAHOO_DRAFT_URL)

		df = pandas.DataFrame()

		get_draft_results(driver, df)
		get_draft_order(df)
		get_player_information(driver, df)
		get_the_real_aho(driver, df)

		store_info(df)

		end_connection(driver)
	else:
		df = get_info()

	plot_draft_results(df, search_drafters=['tim', 'nick'], search_teams=[], search_positions=[])

# Loop through each week and grab the matchup results
def get_weekly_matchup(driver, df):
	for i in range(1,20):
		driver.get('https://hockey.fantasysports.yahoo.com/hockey/31211/matchup?week=' + str(i) + '&module=matchup&mid1=1')
		time.sleep(3)

		html = driver.page_source
		# Fresh bowl of soup
		soup = BeautifulSoup(html)

		pdb.set_trace()

		# TODO - parse the bowl of soup

# Call this function from main to save a history of all matchups
def get_all_matchups():
	print('Getting the history of matchups')

	driver = webdriver.Chrome()
	driver.set_page_load_timeout(60)
	login(driver, settings.YAHOO_MATCHUP_URL)

	df = pandas.DataFrame()

	get_weekly_matchup(driver, df)

def main():
	get_all_matchups()

if __name__ == "__main__":
	main()