from brownie import accounts, config, Election, ElectionManager, network
from time import time
import PySimpleGUI as sg


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def deploy():
    account = get_account()
    my_address = account.address
    sg.Window(title="Elections Canada", layout=[[]], margins=(100, 50)).read()

    return Election.deploy(
        my_address, "TestElection", time() + 9999, {"from": get_account()}
    )


def main():
    deploy()
