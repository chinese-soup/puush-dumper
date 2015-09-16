# puush-dumper

## Usage

```
pip2 install BeautifulSoup requests
```

```
cp config.example.json config.json
```

Edit the config.json file accordingly using your favorite text editor.


```
main.py [-h] [-c CONFIG] [-n] [-p POOL] [-l]

Dump all your files from your puush account.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Alternative path to the config file. Default is
                        ./config.json
  -n, --no-download     Don't download the files, just dump the links to
                        stdout.
  -p POOL, --pool POOL  Change the pool (aka the puush folder) to dump.
                        Optional, as it defaults to your selected default one
                        on puush.me.
  -l, --list-pools      Dump the list of your pools. (aka the puush folder,
                        e.g. Private/Public/Gallery/Custom/...)
```


