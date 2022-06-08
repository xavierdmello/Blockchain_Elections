# Requirements
- [Python](https://www.python.org/downloads/) version greater than `3.7` and less than `3.9.x`. Tested with python `3.9.12`.
- [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/): `python -m pip install pysimplegui`
- [Python-dotenv](https://github.com/theskumar/python-dotenv): `pip install python-dotenv`
- [Brownie](https://github.com/eth-brownie/brownie): `pip install eth-brownie`
- Brownie depends on [ganache](https://github.com/trufflesuite/ganache), install it with [Node.js](https://nodejs.org/en/): `npm install ganache --global`

# Setup
Create a .env file in the root folder with your `PRIVATE_KEY` and `WEB3_INFURA_PROJECT_ID` (if you are connecting to a test network). Your .env file should look similar to this:
  ```
  PRIVATE_KEY=your private key
  WEB3_INFURA_PROJECT_ID=your rpc url
  ```
    
# Usage
Run `scripts/gui.py`.

Standalone packaged `.exe` will be coming soon.
