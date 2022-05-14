# Requirements
- [python](https://www.python.org/downloads/) greater than v3.7 and less than v3.9.x
- [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/): `python -m pip install pysimplegui`
- [brownie](https://github.com/eth-brownie/brownie): `pip install eth-brownie`
- brownie depends on [ganache](https://github.com/trufflesuite/ganache), install it with [Node.js](https://nodejs.org/en/): `npm install ganache --global`

# Setup
Create a .env file in the root folder with your `PRIVATE_KEY`, `WEB3_INFURA_PROJECT_ID` (if you are connecting to a test network), `NETWORK`, and `CONTRACT` (address of the election manager contract). Your .env file should look similar to this:
  ```
  PRIVATE_KEY=your private key
  WEB3_INFURA_PROJECT_ID=your rpc url
  CONTRACT=election manager contract address
  NETWORK=network to connect to
  ```
    
# Usage
Run file with `brownie run`

For example: `brownie run scripts/deploy.py`
