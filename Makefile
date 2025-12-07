.PHONY: install run clean download

# Python interpreter (use venv if active, otherwise assume python3)
PYTHON = python3
PIP = pip

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m streamlit run app.py

clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf data/processed_metrics_cache.pkl

download:
	$(PYTHON) scripts/download_data.py
