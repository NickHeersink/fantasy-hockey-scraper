import pandas as pd
import yahoo_scraper
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

	cats=pd.Series(('G','A','P','PIM','PPP','SHP','GWG','HIT','BLK','W','GAA','SVP','SHO'))
	avgs=pd.Series((20.02083333,35.63194444,55.65277778,32.54861111,16.56944444,0.583333333,3.159722222,68.375,51.4375,2.930555556,2.755486111,0.909708333,0.319444444))

	keys=('Category', 'Average')
	df=pd.concat((cats, avgs), axis=1, keys=keys)
	return df

def get_CPG():
	#get info
	df = pd.read_csv(settings.CSV_FILE_NAME)

	avg_cats = get_cat_avgs() 

	for i, row in df.iterrows():
		df.loc[i,"CPG"] = 0
		if "C" in df.loc[i,"Position"] or "W" in df.loc[i,"Position"]:
			cat_dict = skater_cat_dict
		elif df.loc[i,"Position"] == "G":
			cat_dict = goalie_cat_dict
		for j, col in enumerate(df.columns):
			if col in cat_dict.keys():
				if col != "Games Played" and not math.isnan(df.loc[i,col]):
					if i==15:
						print col
						print 'cuurent: {}'.format(df.loc[i,"CPG"])
						print 'cat val: {}'.format(df.loc[i,col])
						print 'GP: {}'.format(df.loc[i,"Games Played"])
						print 'cat avg: {}'.format(vlookup(avg_cats,cat_dict[col],"Category","Average"))
						print 'dCPG: {}'.format(float(df.loc[i, col])/float(df.loc[i, "Games Played"])/vlookup(avg_cats,cat_dict[col],"Category","Average"))
					dCPG =  float(df.loc[i, col])/float(df.loc[i, "Games Played"])/vlookup(avg_cats,cat_dict[col],"Category","Average")
					df.loc[i,"CPG"] = df.loc[i,"CPG"] + dCPG
					#if i==0: 
						#print 'new val: {}'.format(df.loc[i,"CPG"])
						#print ""
	return df

def vlookup(df, key, key_col, ref_col):
	#grabs the value of the first element in the row
	return df.loc[df[key_col] == key, ref_col].values[0]		

def main():
	df = get_CPG()
	print df[['Player','Games Played','Goals','Assists','Points','Penalty Minutes', 'Blocks','Hits','CPG']]
	del_rows = [] # rows to delete
	for i, row in df.iterrows():
		# if a player has played less than 20 games add them to list of rows to be dropped
		if df.loc[i,"Games Played"] < 20:
			del_rows.append(int(i))

	# delete rows found above
	df = df.drop(del_rows, axis=0)

	#TODO - find a better way to compare goalies and skaters
	#print player with max CPG 
	print df.loc[df['CPG'].idxmax()]

	plt.plot(df["Rank"],df["CPG"],'bo')
	plt.xlabel("Rank")
	plt.ylabel("CPG")
	#plt.show()

if __name__ == "__main__":
	main()