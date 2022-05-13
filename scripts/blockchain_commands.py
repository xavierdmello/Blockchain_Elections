from tkinter import NE
from brownie import accounts, config, network, project
from time import time

# Set the blockchain network here:
NETWORK = "development"

# Load brownie project
p = project.load(name="ElectionsCanada")
p.load_config()
from brownie.project.ElectionsCanada import *
network.connect(NETWORK)

def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def deploy():
    account = get_account()
    my_address = account.address

    return Election.deploy(
        my_address, "TestElection", time() + 9999, {"from": get_account()}
    )
