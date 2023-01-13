# Blockchain Elections

**New! Try it online with my [React frontend](https://github.com/xavierdmello/Blockchain_Elections_React): https://elections.xavierdmello.com**

A proof-of-concept online voting system designed to promote transparency, security, and deter fraud. Created with [Python](https://www.python.org/), [Solidity](https://github.com/ethereum/solidity), [Brownie](https://github.com/eth-brownie/brownie), [Web3.py](https://github.com/ethereum/web3.py), and [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI).

![ElectionsCanada](https://user-images.githubusercontent.com/18093763/174925401-a60b3544-fb70-4803-a520-9a03bd38e107.png)

## Installation
**Windows Users:**
1. Download `ElectionsCanada_Windows.zip` from the [latest release](https://github.com/xavierdmello/Blockchain_Elections/releases/latest)
2. Run `ElectionsCanada.exe`

**MacOS/Linux Users:**
1. Download `Source code (zip)` from the [latest release](https://github.com/xavierdmello/Blockchain_Elections/releases/latest)
2. Make sure you have [Python](https://www.python.org/), [Web3.py](https://pypi.org/project/web3/), and [Python-dotenv](https://pypi.org/project/python-dotenv/) installed
3. Run `ElectionsCanada.py`

## Getting Started 
1. Install a crypto wallet. [Metamask](https://metamask.io/) is recommended. If you already have a wallet, you can skip this step.
2. Enter your wallet address in https://faucet.avax.network/ to get free ETH (test funds) to pay for transaction fees.
3. Click "Add Account" in the Elections Canada app and paste your account's private key.
    - Your private key is not stored securely in the Elections app - while testing it out, please use a seperate account that has no real funds attached to it.
    - In Metamask, you can get your private key by following these steps:
      1. Click the three dots in the top right of Metamask
      2. Click on "Account Details"
      3. Click on "Export Private Key"
4. You're good to go! Create elections, run for office, and vote - with the next generation of secure, decentralized technology.

## Contract Addresses

Deployed on the Avalanche Testnet

`ElectionManager:` [0xC690ce62e557B7e7687DFb58945D49022851621A](https://testnet.snowtrace.io/address/0xC690ce62e557B7e7687DFb58945D49022851621A)

`ElectionDataAggregator:` [0x2A0B10368e69E35a330Fac7DeFcC9dC879e8B021](https://testnet.snowtrace.io/address/0x2A0B10368e69E35a330Fac7DeFcC9dC879e8B021)
