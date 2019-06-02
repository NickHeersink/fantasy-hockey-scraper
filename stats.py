# Return the parameters for a line of best fit
def get_line_of_best_fit_params(x, y):
	xbar = sum(x)/len(x)
	ybar = sum(y)/len(y)

	n = len(x) # or len(Y)

	numer = sum([xi*yi for xi,yi in zip(x, y)]) - n * xbar * ybar
	denum = sum([xi**2 for xi in x]) - n * xbar**2

	b = numer / denum
	a = ybar - b * xbar

	return a, b

def calculate_ssr(n_list, nbar):
	return sum([(n-nbar)**2 for n in n_list])

def calculate_sse(n_list, nhat_list):
	return sum([(n-nhat)**2 for n, nhat in zip(n_list, nhat_list)])

def calculate_coeff_determination(x, y, yhat):
	ybar = sum(y) / len(y) # Mean of y

	ssr = calculate_ssr(y, ybar)
	sse = calculate_sse(y, yhat)

	ssto = ssr + sse

	return float(ssr) / float(ssto)
