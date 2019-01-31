# New-hope
a bot for Waves-blockchain game: https://www.multi-pass.club/
Bot made  with pywaves library

## What needed to run a bot?
Python: https://www.python.org, pywaves library and a cron job

## Instalation
```
pip pywaves
```
Then in pywaves folder(for unix /home/user/.local/lib/python3.6/site-packages/pywaves) replace address.py with address.py from this project

## Start
To start a bot first of all need to input config:
```
yourPrivateKey = '' #Put in brackets yourPrivateKey
yourAddress = '' #put in brackets yourAddress
betBlock = 3 #instead of 3 put a number when you want to make a bet
```
Then ```python3 NewHope.py``` and if everything is ok now. Setup a cron job to do this command ```python3 NewHope.py```
