from selenium import webdriver

import settings
import time


def login(driver):
	driver.get(settings.YAHOO_URL)

	username = driver.find_element_by_name('username')
	username.send_keys(settings.YAHOO_USERNAME)
	driver.find_element_by_id('login-signin').click()

	time.sleep(10)

	password = driver.find_element_by_name('password')
	password.send_keys(settings.YAHOO_PASSWORD)
	driver.find_element_by_id('login-signin').click()

def get_draft_results(driver):
	draft_order = ['bohan', 'nico', 'calvin', 'nick', 'tim', 'joel', 'jeremy', 'nate']
	draft_order = draft_order + draft_order[::-1]

	player_web_elem_list = driver.find_elements_by_class_name('name')
	player_list = [player.text for player in player_web_elem_list]

	draft_order_list = draft_order*13

def make_connection():
	driver = webdriver.Chrome()
	driver.set_page_load_timeout(60)

	login(driver)

	get_draft_results(driver)

	driver.close()

def main():
	print('Welcome to the Non-Competitive Action League')
	
	make_connection()


if __name__ == "__main__":
	main()