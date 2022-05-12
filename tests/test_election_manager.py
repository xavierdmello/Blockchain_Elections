import pytest
from brownie import ElectionManager
from scripts.deploy import get_account
from time import time


def test_creating_elections():
    account = get_account()
    address = account.address
    election_manager = ElectionManager.deploy({"from": account})

    election_manager.createElection("E1", time(), {"from": account})
    election_manager.createElection("E2", time(), {"from": account})
    election_manager.createElection("E3", time(), {"from": account})
    election_manager.createElection("Rainbow Ponies", time(), {"from": account})

    electionNames = election_manager.getElectionNames()
    assert electionNames[0] == "E1"
    assert electionNames[1] == "E2"
    assert electionNames[2] == "E3"
    assert electionNames[3] == "Rainbow Ponies"
