all: json

json: fit.json

.PHONY: all json

fit.json: fit.csv fit_to_json.py
	fit_to_json.py

