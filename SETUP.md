# Setup

First, download the repo. 

Second, setup a virtual environment to install packages. Refer to [python docs](https://docs.python.org/3/library/venv.html) to determine your source activation command.
```bash
python3 -m venv venv
source venv/Scripts/activate # on Windows
pip3 install -r requirements.txt
```

Third, create a the config.py file `lolassethelper/config.py`. Copy the `config.example.py` file, remove the example from the file name and insert all the requested values

After that, you can already run the script (currently it only supports challenges):
```bash
python3 -m lolassethelper.challenges
```
The generated files should be in a `output/` directory.