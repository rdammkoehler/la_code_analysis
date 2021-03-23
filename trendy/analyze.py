def analyze(data):
	result = 'undetermined'
	if data and len(data) > 1:
		if data[-1][1] > data[0][1]:
			return 'problematic'
		if data[-1][1] <= data[0][1]:
			return 'satisfactory'
	return result
