from selenium import webdriver

import pickle
import settings
import stats
import time

import matplotlib.pyplot as plt
import numpy as np

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

def get_draft_order():
	draft_order = SETTINGS.DRAFT_ORDER
	draft_order = draft_order + draft_order[::-1]

	draft_order *= 13

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

# Store info in .dat file
def store_info(players, draft_order, ranks):
	with open('data.pickle', 'wb') as file:
		pickle.dump(players, file)
		pickle.dump(draft_order, file)
		pickle.dump(ranks, file)

# Retrieve stored info from .dat file
def get_stored_info():
	file = open('data.pickle', 'rb')		
	players = pickle.load(file)
	draft_order = pickle.load(file)
	ranks = pickle.load(file)

	return players, draft_order, ranks

def get_player_lists_by_person(person, players, draft_order):
	return [player for index, player in enumerate(players) if person == draft_order[index]]

def get_player_ranks_by_person(person, players, personal_players, ranks):
	return [rank for index, rank in enumerate(ranks) if players[index] in personal_players]

def get_draft_spots_by_person(person, players, personal_players, draft_spots):
	return [draft_spot for index, draft_spot in enumerate(draft_spots) if players[index] in personal_players]

# Plot the results
def plot_draft_results(players, draft_order, draft_spots, ranks):
	ranks = [int(rank) for rank in ranks] # Convert strings to integers

	fig = plt.figure()
	ax = fig.add_subplot(111)

	for person in settings.DRAFT_ORDER:
		personal_players = get_player_lists_by_person(person, players, draft_order)
		personal_ranks = get_player_ranks_by_person(person, players, personal_players, ranks)
		personal_draft = get_draft_spots_by_person(person, players, personal_players, draft_spots)

		ax.scatter(personal_draft, personal_ranks, label=person)

	a, b = stats.get_line_of_best_fit_params(draft_spots, ranks)

	yhat = [a + b*x for x in draft_spots]

	r_squared = stats.calculate_coeff_determination(draft_spots, ranks, yhat)

	plt.plot(draft_spots, yhat)

	plt.legend(loc='upper left')
	plt.xlabel('Draft Position')
	plt.ylabel('Ranking')
	plt.title('R-squared value: ' + str(r_squared))

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

		store_info(players, draft_order, ranks)
	
		end_connection(driver)
	else:
		players, draft_order, ranks = get_stored_info()

	draft_spots = np.arange(1,209)
	plot_draft_results(players, draft_order, draft_spots, ranks)


if __name__ == "__main__":
	main()