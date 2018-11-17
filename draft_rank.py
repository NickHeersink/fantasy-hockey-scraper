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
	player_list = [for name in driver.find_element_by_id()]


def make_connection():
	driver = webdriver.Chrome()
	driver.set_page_load_timeout(60)

	login(driver)

	get_draft_results(driver)


def main():
	print('Welcome to the Non-Competitive Action League')
	
	make_connection()


if __name__ == "__main__":
	main()