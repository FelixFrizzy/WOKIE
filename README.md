# WOKIE
![tests](https://github.com/FelixFrizzy/WOKIE/actions/workflows/tests.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

WOKIE (**W**ell-translated **O**ptions for **K**nowledge Management in **I**nternational **E**nvironments) is a free, open-source tool that automatically translates SKOS thesauri into multiple languages. It combines online translation services with LLMs to pick the best translation for each term. WOKIE runs on any standard PC, making it easy to create FAIR (Findable, Accessible, Interoperable, Reusable) and multilingual vocabularies.
For an overview of services, see [supported services](supported-services.md). 

**Demo**: If you want to quickly try it out, you can jump to the Demo example section and use Option 1 (binary file including all dependencies). 

# Prerequisites
- In case you want to use any of the non-free services, set up the required API_KEYS (see .env.template).
- In case you want to use Argos as offline translator, install its local running API with `pip install libretranslate` and run it with `libretranslate --load-only ar,de,en,es,fr,hu,it,nb,nl,pt,ru,sl`. Add other languages if you need them. **Caution**: this does not work with Python 3.13.x (as of 01.05.2025).
- Install a JavaScript runtime, nodejs is recommended (`sudo apt-get install nodejs` for Debian/Ubuntu or `brew install nodejs`for MacOS)


# How to install
- Tested with Python 3.11.12 on MacOS 15 and on Debian 12.

1. Create a virtual Python environment.
2. `pip3 install -r requirements.txt`
3. `cp .env.template .env`
4. Add API secrets and other required environment variables (depending on which services you want to use) to `.env`.

# How to run
## Command-line arguments
See `python main.py --help`.

## Command structure
`python main.py --input inputfile.rdf --language "en" --context "Digital Humanities" --threshold 0.6 --primary_translation lingvanex google modernmt microsoft yandex argos reverso ponspaid --secondary_translation "gemini-2.0-flash" --min_primary_translations 5`

## Demo example
It is possible to try the code out without configuring any api_keys, by using only free translation services for demonstration purposes. There are the following restrictions:
- All of the implemented LLMs require an API-Key. Therefore, only a Dummy LLM is used to make the example possible.
- Only two primary translation services are used in this demo. All the ones needing API-Keys or depend on locally running services are not used in the demo.
- To show real translations (although of limited quality due to fewer primary services and lack of LLM-based refinement), we set `threshold` to 0 and `min_primary_translations` to 1 in this case. This means that the refinement will not be done. 
### Provided sample files
- TaDiRAH where the German language was removed: `sample-files/tadirah_de-missing.rdf`
- DYAS where the English language was removed: `sample-files/dyas_en-missing.rdf`
### Run the demo
#### Option 1 (run static binary, dependencies included, slower)
- We created binary files which have python and all dependencies included for quickly running the code as demo.
- For Linux / Macos / Windows with WSL:
    - Only prerequisite: Install `nodejs` on your system (e.g. `sudo apt-get install nodejs` or `brew install node`)
    - Download the binary file matching your OS and CPU architecture: [wokie_64 for Linux or Windows (with WSL)](https://sourceforge.net/projects/wokie/files/wokie_x64/download) or for Apple Silicon Chips [wokie_arm](https://sourceforge.net/projects/wokie/files/wokie_arm/download).
    - Put the file into this folder.
    - Execute `chmod +x <wokie>`
    - Run one of these commands and replace <wokie> with the download file, start up takes a while due to unpacking:
    - `./wokie_<arch> --input sample-files/tadirah_de-missing.rdf --language "de" --context "Digital Humanities" --threshold 0.0 --primary_translation lingvanex modernmt --secondary_translation "dummy" --min_primary_translations 1`
    - `./wokie_<arch> --input sample-files/dyas_en-missing.rdf --language "en" --context "Digital Humanities" --threshold 0.0 --primary_translation lingvanex modernmt --secondary_translation "dummy" --min_primary_translations 1`
- For Windows with native Python:
    - JavaScript runtime (e.g. nodejs) might be necessary.
    - Download [wokie.exe](https://sourceforge.net/projects/wokie/files/wokie.exe/download).
    - Put the file into this folder.
    - Run one of these commands, start up takes a while due to unpacking:
    - `wokie.exe --input sample-files/tadirah_de-missing.rdf --language "de" --context "Digital Humanities" --threshold 0.0 --primary_translation lingvanex modernmt --secondary_translation "dummy" --min_primary_translations 1`
    - `wokie.exe --input sample-files/dyas_en-missing.rdf --language "en" --context "Digital Humanities" --threshold 0.0 --primary_translation lingvanex modernmt --secondary_translation "dummy" --min_primary_translations 1`
#### Option 2 (more flexible, requires to install dependencies)
- Only installing `nodejs` and `pip install -r requirements.txt` is needed for the demo (using a Python virtual environment is recommended).
- Run one of these commands (or both if you like):
`python main.py --input sample-files/tadirah_de-missing.rdf --language "de" --context "Digital Humanities" --threshold 0.0 --primary_translation lingvanex modernmt --secondary_translation "dummy" --min_primary_translations 1`
`python main.py --input sample-files/dyas_en-missing.rdf --language "en" --context "Digital Humanities" --threshold 0.0 --primary_translation lingvanex modernmt --secondary_translation "dummy" --min_primary_translations 1`
- Inspect the `<inputfilename>_updated.rdf` files in the `sample-files` folder to see the terms translated to German / English as soon as the command finished.

# Developer Info
- Enable logging with `python main.py ... --enable-logging`.
- Run translator services individually for testing: e.g. `python -m modules.primary_translators.modernmt_translator`.
- Enable Debug mode in .env: Debug=True also logs INFO events and changes the output file name to be more descriptive (and therefore longer), including timestamps. 

## How to use own translation services
You can implement your own translation services under modules/primary_translators and modules/secondary_translators. See abstract base class for more info.

## Tests
- Run `pytest tests/test_integration.py` in main folder to run integration test.
- Run `pytest test_translation_services.py`  for API tests (requires secrets in `.env`) and might consume a small number of tokens of paid APIs. This is excluded by default when running `pytest` using `pytest.ini`.

# License Information
## Used vocabularies: 
- [TaDiRAH](https://vocabs.acdh.oeaw.ac.at/tadirah/en/) (adapted) [[CC0](https://creativecommons.org/publicdomain/zero/1.0/); Creators: Luise Borek, Canan Hastik, Vera Khramova, Jonathan Geiger]
- [DYAS](https://isl.ics.forth.gr/bbt-federated-thesaurus/HUMANITIES-THESAURUS/en/) (adapted) [[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en); Creators: Chatzi Maria (ASFA); Chatzimichail Christos (AA); Chrysovitsanos Gerasimos (AA); Daskalothanasis Nikos (ASFA); Dimakopoulou Christina (ASFA); Drapelova Pavla (UOA); Falierou Anastasia (AA); Gardika Katerina (UOA); Georgopoulos Theodoros (UOA); Goulis Helen (AA); Iakovidou Athena (AA); Kalafata Patritsia (AA); Karasimos Athanasios (AA); Katakis Stelios (UOA); Katsiadakis Helen (AA); Konstantellou Dora (UOA); Mergoupi-Savaidou Eirini (AA); Papadopoulou Georgia (UOA); Sichani Anna-Maria (AA); Sinou Christina (AA); Souyioultzoglou Iraklitos (AA); Terzis Christos (AA); Theodoridou Dimitra (UOA); Tzedopoulos Giorgos (AA); Xiropaidis Georgios (ASFA); ]  

## WOKIE
WOKIE is licensed under the Apache License, Version 2.0. 
License owner: Karlsruhe Institute of Technology (KIT)

# Contact information
- Creator: Felix Kraus
- Email (substitute accordingly): firstname.lastname (at) kit (dot) edu
- License owner: Karlsruhe Institute of Technology (KIT)

# Acknowledgement
Development of this software product was funded by the research program “Engineering Digital Futures” of the Helmholtz Association of German Research Centers and the Helmholtz Metadata Collaboration Platform (HMC).