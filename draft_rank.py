import time

import pandas
import matplotlib.pyplot as plt

from selenium import webdriver

import settings
import stats

# Connect to Yahoo Fantasy
def login(driver):
	driver.get(settings.YAHOO_DRAFT_URL)

	username = driver.find_element_by_name('username')
	username.send_keys(settings.YAHOO_USERNAME)
	driver.find_element_by_id('login-signin').click()

	time.sleep(10)

	password = driver.find_element_by_name('password')
	password.send_keys(settings.YAHOO_PASSWORD)
	driver.find_element_by_id('login-signin').click()

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

		time.sleep(10)

		table = driver.find_element_by_class_name('players-table')
		rows = table.find_elements_by_tag_name('tr')

		# The current ranking can be found in column 2, row 6.
		columns = rows[2].find_elements_by_tag_name('td')
		df.loc[index, 'Rank'] = columns[6].text

		# TODO - add team (column 3)
		# TODO - add position (column 1 - split after hyphen)

		print('Ranking is: ' + df.loc[index, 'Rank'])

def get_the_real_aho(driver, df):
	driver.get(settings.YAHOO_RANK_URL)

	search_box = driver.find_element_by_id('playersearchtext')

	search_box.clear()
	search_box.send_keys('Sebastian Aho')
	search_box.send_keys(u'\ue007') # Press enter - TODO replace with clicking 'Search' button

	time.sleep(10)

	table = driver.find_element_by_class_name('players-table')
	rows = table.find_elements_by_tag_name('tr')

	# The real Sebastian Aho can be found in column 6, row 3!!!!!!!
	columns = rows[3].find_elements_by_tag_name('td')
	df.loc[df.index.values[df.Player == 'Sebastian Aho'], 'Rank'] = columns[6].text

# Store info in .csv file using Pandas
def store_info(df):
	df.to_csv(settings.CSV_FILE_NAME)

def get_info():
	return pandas.read_csv(settings.CSV_FILE_NAME, index_col=0)

def get_player_lists_by_person(df, person):
	return df.Player[df.Drafter == person]

def get_player_ranks_by_person(df, person):
	return df.Rank[df.Drafter == person]

def get_draft_spots_by_person(df, person):
	return df.index.values[df.Drafter == person]

# Get the residuals and add a column to the Pandas dataframe
def calculate_residuals(df, expected_ranks):
	residuals = [expected_rank - actual_rank for expected_rank, actual_rank in zip(expected_ranks, df.Rank)]

	# 'Normalize' ranks so that the further ones are less costly
	df['Residual'] = [residual for index, residual in enumerate(residuals)]

def add_large_residuals(df, ax):
	worst_players = df.nsmallest(3, 'Residual')
	best_players = df.nlargest(3, 'Residual')

	for player in best_players.itertuples():
		ax.annotate(player.Player, xy=(player.Index, player.Rank), textcoords = 'data')

	for player in worst_players.itertuples():
		ax.annotate(player.Player, xy=(player.Index, player.Rank), textcoords = 'data')

# Plot the results
def plot_draft_results(df):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	for person in settings.DRAFT_ORDER:
		personal_players = get_player_lists_by_person(df, person)
		personal_ranks = get_player_ranks_by_person(df, person)
		personal_draft = get_draft_spots_by_person(df, person)

		ax.scatter(personal_draft, personal_ranks, label=person)

	a, b = stats.get_line_of_best_fit_params(df.index.values, df.Rank)

	df['Expected'] = [a + b*x for x in df.index.values]

	residuals = calculate_residuals(df, df['Expected'])

	r_squared = stats.calculate_coeff_determination(df.index.values, df.Rank, df.Expected)

	plt.plot(df.index.values, df.Expected)

	plt.legend(loc='upper left')
	plt.xlabel('Draft Position')
	plt.ylabel('Ranking')
	plt.title('R-squared value: ' + str(r_squared))

	add_large_residuals(df, ax)

	plt.show()

# Clean up the Chrome webdriver
def end_connection(driver):
	driver.close()

def main():
	print('Welcome to the Non-Competitive Action League')

	if settings.NEED_NEW_DATA:
		driver = webdriver.Chrome()
		driver.set_page_load_timeout(60)
		login(driver)

		df = pandas.DataFrame()

		get_draft_results(driver, df)
		get_draft_order(df)
		get_player_information(driver, df)
		get_the_real_aho(driver, df)

		store_info(df)

		end_connection(driver)
	else:
		df = get_info()

	plot_draft_results(df)


if __name__ == "__main__":
	main()