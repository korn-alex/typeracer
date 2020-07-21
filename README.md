# typeracer
Storing www.typeracer.com stats in a local database while typing without an account using selenium.
Supports Linux/Windows

# Using
After successfull installation start `run.py` or the created exe on Windows.
On the first run a config file will be created and a chromedriver will be downloaded.
After that, chrome browser will be opened with www.typeracer.com ready to go.

# Requirements
- installed chrome browser
- python 3

# Installation
1. create virtual environment

    `python -m venv .env`

2. activate environment

    **Linux**:
    `. .env/bin/activate`

    **Windows**
    `.env/Scripts/activate.ps1`

3. install dependencies

    `pip install -r requirements.txt`


4. (optional on windows) create exe

    execute `make_exe.bat`
