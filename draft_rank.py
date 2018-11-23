from selenium import webdriver

import pickle
import settings
import time

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
	draft_order = ['bohan', 'nico', 'calvin', 'nick', 'tim', 'joel', 'jeremy', 'nate']
	draft_order = draft_order + draft_order[::-1]

	players_web_elems = driver.find_elements_by_class_name('name')
	players = [player.text for player in players_web_elems]

	draft_order *= 13

	return players, draft_order

def get_player_ranks(driver, players):
	print('hi')

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
	draft_order = []
	ranks = []
	#draft_order = pickle.load(file)
	#ranks = pickle.load(file)

	return players, draft_order, ranks

# Plot the results
def plot_draft_results(players, draft_order):
	print('hello')

# Login to the Yahoo site
def make_connection(driver):
	login(driver)

# Clean up the Chrome webdriver
def end_connection(driver):
	driver.close()

def main():
	print('Welcome to the Non-Competitive Action League')

	# Set this to pull new data
	need_new_data = False

	if need_new_data:
		driver = webdriver.Chrome()
		driver.set_page_load_timeout(60)
		make_connection(driver)

		players, draft_order = get_draft_results(driver)
		ranks = get_player_ranks(driver, players)

		store_info(players, draft_order, ranks)
	
		end_connection(driver)
	else:
		players, draft_order, ranks = get_stored_info()

	plot_draft_results(players, draft_order)


if __name__ == "__main__":
	main()