create_environment:
	conda env create -f environment.yaml
	. activate slamdring; pip install -e .

destroy_environment:
	conda remove --name slamdring --all

data/test_data_large.csv:
	python scripts/make_requests.py
