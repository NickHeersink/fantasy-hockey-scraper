import os
import pdb
from selenium import webdriver

def player_data(season):

	#set-up driver
	driver = webdriver.Chrome()
	driver.set_page_load_timeout(600)
	
	#grab info from web-page
	driver.get("https://www.hockey-reference.com/leagues/NHL_"+season+"_skaters.html")
	div_stats = driver.find_element_by_id('div_stats')
	

	# extract just text and convert to human readable
	csv_text = div_stats.text.encode('utf-8')
	csv_text = csv_text.replace(' ',',')

	driver.close()

	#will create a new file if can't find one with this name
	f = open(season+'_player.csv','w+')
	f.write(csv_text)
	f.close()

if __name__ == "__main__":
	player_data('2019')