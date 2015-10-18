# puush-dumper

## TODO
* allow saving files with their original name (like puush allows to)
* implement --output-directory (currently hardcoded to puush_files in script's folder)
* implement output directory in config file
* implement arguments that override the username and password that are loaded from config file
* exceptions
* cleanup

## How to install

### Step 0
```
pip2 install BeautifulSoup requests
```

### Step 1
```
git clone git@github.com:chinese-soup/puush-dumper.git
cp puush-dumper/config.example.json puush-dumper/config.json
```
### Step 2
Edit the config.json file accordingly using your favorite text editor.

### Step 3
```
python2 main.py
```

## Usage
```
usage: main.py [-h] [-c CONFIG] [-o OUTPUT_DIRECTORY] [-n] [-f TEXT_OUTPUT]
               [-p POOL] [-l]

Dump all your files from your puush account.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Alternative path to the config file. Default is
                        ./config.json
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Override's config output folder to download to.
  -n, --no-download     Don't download the files, just dump the links.
                        Defaults to stdout, use with -f to .
  -f TEXT_OUTPUT, --text-output TEXT_OUTPUT
                        Provide a filename to dump the links to.
  -p POOL, --pool POOL  Change the pool (aka the puush folder) to dump.
                        Optional, as it defaults to your selected default one
                        on puush.me.
  -l, --list-pools      Dump the list of your pools. (aka the puush folder,
                        e.g. Private/Public/Gallery/Custom/...)
```


