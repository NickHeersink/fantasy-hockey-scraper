from selenium import webdriver

import pickle
import settings
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
	draft_order = ['bohan', 'nico', 'calvin', 'nick', 'tim', 'joel', 'jeremy', 'nate']
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

	return ranks

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

# Plot the results
def plot_draft_results(players, draft_order):
	print('hello')

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

	plot_draft_results(players, draft_order)


if __name__ == "__main__":
	main()