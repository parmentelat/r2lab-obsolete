TOOL = configure.py

all: config

config: fit.json 

.PHONY: all config

fit.json: $(TOOL) fit.csv 
	$(TOOL) fit.csv
