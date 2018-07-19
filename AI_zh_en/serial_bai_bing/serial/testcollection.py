import re

def to_list():
	result=[]
	fd = file( "collection.txt", "r" )
	for line in fd.readlines():
		result.append(list(line.lower().split(',')))
	print(result)
	 
	for item in result:
		for it in item:
		   print it
	
	return result
	   
def fuzzyfinder(result):
	suggestions = []
	pattern = '.*'.join('h') # Converts 'djm' to 'd.*j.*m'
	regex = re.compile(pattern)     # Compiles a regex.
	for item in result:
		for it in item:
			match = regex.search(it)  # Checks if the current item matches the regex.
			if match:
				suggestions.append(it)
		
	print("----------------")	
	print(suggestions)
	print("----------------")
	return suggestions

		
if __name__ == "__main__":
	
	list_s = to_list()
	
	fuzzyfinder(list_s)