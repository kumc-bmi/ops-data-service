all: run

run:
	 . ~/.allofus/.env && \
	python3 ops_data_api.py
	wc -l *.csv


clean:
	rm -rf *.csv
