# WOKIE

# General info
- Tested with python 3.11.7. and 3.11.11 on MacOS 15

# Prerequisits
- Set up translation services that require API_KEYS (see .env.template)
- Install Ollama app and run it if you want to use local models
- install libretranslate (pip install libretranslate) and run it with `libretranslate --load-only ar,de,en,es,fr,hu,it,nb,nl,pt,ru,sl` if you want to use argos translate. caution: this does not work with python 3.13.x (as of 01.05.2025)

# How to install

1. Create virtual python environment
2. `pip3 install -r requirements.txt
3. `ollama pull llama3.2 deepseek-r1:1.5b`
4. `cp .env.template .env`
5. Add API secrets to `.env`

# How to run
## vars
see `python main.py --help`

## Example run
`python translateontology.py --input inputfile.rdf --language "en" --context "Digital Humanities" --threshold 0.6 --primary_translation "google" --secondary_translation "openai" --model "gpt-3.5-turbo"`
`python main.py --input inputfile.rdf --language "en" --context "Digital Humanities" --threshold 0.6 --primary_translation google modernmt reverso --secondary_translation "gpt-3.5-turbo" --secondary_strategy individual`

# Developer infos
- enable logging with `python main.py ... --enable-logging`
- run translator services individually for testing: e.g. `python -m modules.primary_translators.modernmt_translator`

## How to use own translation services
You can implement you own translation services under modules/primary_translators and modules/secondary_translators. See abstract base class for more info.
## tests
- run `pytest tests/test_integration.py` in main folder to run integration test
- run `pytest test_translation_services.py`  for API tests (requires secrets in `.env`) and might consume very little Tokens of paid APIs. This is excluded by default when running `pytest`
- run `pytest `--cov=. --cov-report=xml` if you use a coverage extension in your IDE that uses coverage.xml reports (e.g. gutter extension in VSCode)

# 

**License**

WOKIE is licensed under the Apache License, Version 2.0. 
License owner: Karlsruhe Institute of Technology (KIT)

**Acknowledgement**
Development of this software product was funded by the research program “Engineering Digital Futures” of the Helmholtz Association of German Research Centers and the Helmholtz Metadata Collaboration Platform (HMC)