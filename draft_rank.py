import time

import pickle
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
def get_draft_results(driver):
	players_web_elems = driver.find_elements_by_class_name('name')
	players = [player.text for player in players_web_elems]

	return players

# Gets draft order (can be done offline knowing the order repeats)
def get_draft_order():
	draft_order = settings.DRAFT_ORDER
	draft_order = draft_order + draft_order.reverse()

	draft_order *= 13 # order repeats 13 times

	return draft_order

# Get the player rankings from the player page
def get_player_ranks(driver, players):
	driver.get(settings.YAHOO_RANK_URL)

	search_box = driver.find_element_by_id('playersearchtext')

	ranks = []

	for index, player in enumerate(players):
		print player

		search_box.clear()
		search_box.send_keys(player)
		search_box.send_keys(u'\ue007') # Press enter - TODO replace with clicking 'Search' button

		time.sleep(10)

		table = driver.find_element_by_class_name('players-table')
		rows = table.find_elements_by_tag_name('tr')

		# The current ranking can be found in column 2, row 6.
		columns = rows[2].find_elements_by_tag_name('td')
		ranks.append(columns[6].text)

		print('Ranking is: ' + ranks[index])

	return [int(rank) for rank in ranks] # Returns a list of integers instead of strings

# Store info in .csv file using Pandas
def store_info(players, draft_order, ranks):
	fantasy_data = list(zip(players, draft_order, ranks))

	df = pandas.DataFrame(data=fantasy_data, columns=['Player', 'Drafter', 'Rank'])
	df.to_csv(settings.CSV_FILE_NAME)

	return df

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

		players = get_draft_results(driver)
		draft_order = get_draft_order()
		ranks = get_player_ranks(driver, players)

		df = store_info(players, draft_order, ranks)

		end_connection(driver)
	else:
		df = get_info()

	plot_draft_results(df)


if __name__ == "__main__":
	main()