import pandas as pd
import hockey_reference_scraper as hrs
import yahoo_scraper as ys
import settings
import math
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

skater_cat_dict = {
	"Goals": "G",
	"Assists": "A",
	"Points": "P",
	"Penalty Minutes": "PIM",
	"Blocks": "BLK",
	"Hits": "HIT"
}

goalie_cat_dict = {
	"Wins": "W",
	"Save Percentage": "SVP",
	"Goals Against Average": "GAA",
	"Shutouts": "SHO"	
}

cat_dict = {
	"Games Played": "GP",
	"Goals": "G",
	"Assists": "A",
	"Points": "P",
	"Penalty Minutes": "PIM",
	"Blocks": "BLK",
	"Hits": "HIT",
	"Games Played": "GP",
	"Wins": "W",
	"Save Percentage": "SVP",
	"Goals Against Average": "GAA",
	"Shutouts": "SHO"	
}

def get_cat_avgs():

	
	try:
		df = pd.read_excel(r'C:\Users\nicos\Documents\Projects\HockeyDA\Book1.xlsx','Stat Weighting')
	except IOError:
		cats=pd.Series(('G','A','P','PIM','PPP','SHP','GWG','HIT','BLK','W','GAA','SVP','SHO'))
		avgs=pd.Series((20.02083333,35.63194444,55.65277778,32.54861111,16.56944444,0.583333333,3.159722222,68.375,51.4375,2.930555556,2.755486111,0.909708333,0.319444444))

		keys=('Category', 'Average')
		df=pd.concat((cats, avgs), axis=1, keys=keys)
	return df

def get_CPG(df):

	avg_cats = get_cat_avgs() 

	for i, row in df.iterrows():
		df.loc[i,"CPG"] = 0
		if df.loc[i,"Position"] == "G":
			#TODO - find a better way to do CPG for goalies
			cat_dict = goalie_cat_dict
		else:
			cat_dict = skater_cat_dict
		for j, col in enumerate(df.columns):
			if col in cat_dict.keys():
				if col != "Games Played" and not math.isnan(df.loc[i,col]):
					
					if col == "Save Percentage":
						dCPG = (float(df.loc[i, col])-vlookup(avg_cats,cat_dict[col],"Category","Average"))/vlookup(avg_cats,cat_dict[col],"Category","Average")
					elif col =="Goals Against Average":
						dCPG = (vlookup(avg_cats,cat_dict[col],"Category","Average")-float(df.loc[i, col]))/vlookup(avg_cats,cat_dict[col],"Category","Average")/9
					else:
						dCPG =  float(df.loc[i, col])/float(df.loc[i, "Games Played"])/vlookup(avg_cats,cat_dict[col],"Category","Average")
						if col == "Wins" or col == "Shutouts":
							dCPG=dCPG/9
					
					df.loc[i,"CPG"] = df.loc[i,"CPG"] + dCPG
					

	return df

def get_roster(team_name,df=None):
	if df is None:
		df = pd.read_csv(settings.CSV_FILE_NAME)
	
	del_rows = [] # rows to delete
	for i, row in df.iterrows():
		# if a player has played less than 20 games add them to list of rows to be dropped
		if df.loc[i,"Drafter"] != team_name:
			del_rows.append(int(i))	
	# delete rows found above
	df = df.drop(del_rows, axis=0)

	return df

def find_trade(team_A,team_B,metric_A,metric_B):
	trade = []
	trade_value_A = 0
	trade_value_B = 0

	for a, row in team_A.iterrows():
		for b, row in team_B.iterrows():
			value_A = team_B.loc[b,metric_A]-team_A.loc[a,metric_A]
			value_B = team_A.loc[a,metric_B]-team_B.loc[b,metric_B]

			if (value_A > trade_value_A and value_B > 0) or (value_A == trade_value_A and value_B > trade_value_B):
				trade_value_A = value_A
				trade_value_B = value_B
				trade = [team_A.loc[a,"Player"],team_B.loc[b,"Player"]]

	return trade

def find_trades(df,team_A_name,metric_A,metric_B,team_col=None):
	if team_col is None:
		team_col = "Drafter"

	# initiate trades dataframe
	trades = pd.DataFrame(columns = ['Player A','Team B','Player B'])
	# get players on Team A
	team_A = get_roster(team_A_name,df)

	del_rows = [] # rows to delete
	for i, row in df.iterrows():
		# remove players on Team A
		if df.loc[i,team_col] == team_A_name:
			del_rows.append(int(i))	
	# delete rows found above
	df = df.drop(del_rows, axis=0)

	for a, row in team_A.iterrows():
		for b, row in df.iterrows():
			value_A = df.loc[b,metric_A]-team_A.loc[a,metric_A]
			value_B = team_A.loc[a,metric_B]-df.loc[b,metric_B]

			if value_A > 0 and value_B > 0:
				#trade = pd.DataFrame({"Player A":team_A.loc[a,"Player"], 
                #        			  "Team B":df.loc[b,team_col],
                #         			  "Player B":df.loc[b,"Player"]}) 
				#trades.append(trade)
				trades.loc[len(trades)] = [team_A.loc[a,"Player"],df.loc[b,team_col],df.loc[b,"Player"]]

	return trades
			

#================================= Utility Functions =================================

def vlookup(df, key, key_col, ref_col):
	#grabs the value of the first element in the row
	return df.loc[df[key_col] == key, ref_col].values[0]	

def plot(x,y,xlabel,ylabel):
	plt.plot(x,y,'bo')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.show()	

def update_player_info():
	hrs.main()

#================================= Testing Functions =================================

def get_best_CPG():
	#get info
	df = pd.read_csv(settings.CSV_FILE_NAME)

	df = get_CPG(df)
	#print df[['Player','Games Played','Goals','Assists','Points','Penalty Minutes', 'Blocks','Hits','CPG']]
	del_rows = [] # rows to delete
	for i, row in df.iterrows():
		# if a player has played less than 20 games add them to list of rows to be dropped
		if df.loc[i,"Games Played"] < 20:
			del_rows.append(int(i))

	# delete rows found above
	df = df.drop(del_rows, axis=0)

	#GOALIE STUFF
	#plot(df["Wins"]/df["Games Played"], df["Save Percentage"], "Win Percentage", "SVP")
	#print df.sort_values(by=['CPG'])[["Player","Games Played","Wins","Goals Against Average","Save Percentage","Shutouts","CPG"]]

	#print player with max CPG 
	#print df.loc[df['CPG'].idxmax()]
	print df.sort_values(['CPG'], ascending=False).head(20)[['Player','Games Played','CPG']]

def find_good_trade(team_A_name,team_B):

	team_A = get_roster(team_A_name)
	team_A = get_CPG(team_A)
	del_rows = [] # rows to delete
	for i, row in team_A.iterrows():
		# if a player has played less than 20 games add them to list of rows to be dropped
		if team_A.loc[i,"Position"] == 'G' or team_A.loc[i,"Games Played"] < 20:
			del_rows.append(int(i))

	# delete rows found above
	team_A = team_A.drop(del_rows, axis=0)

	team_B = get_roster(team_B_name)
	team_B = get_CPG(team_B)
	del_rows = [] # rows to delete
	for i, row in team_B.iterrows():
		# if a player has played less than 20 games add them to list of rows to be dropped
		if team_B.loc[i,"Position"] == 'G' or team_B.loc[i,"Games Played"] < 20:
			del_rows.append(int(i))

	# delete rows found above
	team_B = team_B.drop(del_rows, axis=0)

	team_A["PPG"] = team_A["Points"]/team_A["Games Played"]
	team_B["PPG"] = team_B["Points"]/team_B["Games Played"]

	trade = find_trade(team_A,team_B,"CPG","PPG")

	#print stats
	print team_A.loc[team_A['Player']==trade[0]]
	print team_B.loc[team_B['Player']==trade[1]]

def main():
	df = pd.read_csv(settings.CSV_FILE_NAME)
	df = get_CPG(df)
	df['PPG'] = df['Points']/df["Games Played"]
	trades = find_trades(df,'nico','CPG','PPG')

	print trades

if __name__ == "__main__":
	main()