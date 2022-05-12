# Requirements
- [brownie](https://github.com/eth-brownie/brownie)

# Setup
Create a .env file in the root folder with your `PRIVATE_KEY` and `WEB3_INFURA_PROJECT_ID` (if you are connecting to a test network). Your .env file should look similar to this:
  ```
  PRIVATE_KEY=your private key
  WEB3_INFURA_PROJECT_ID=your rpc url
  ```
    
# Usage
Run file with `brownie run`

For example: `brownie run scripts/deploy.py`
