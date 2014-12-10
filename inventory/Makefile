all: json

json: fit.json 

.PHONY: all json

fit.json: fit_to_json.py fit.csv 
	fit_to_json.py fit.csv

