from brownie import ElectionManager, accounts
from scripts.blockchain import load_accounts_from_dotenv
from time import time


def test_creating_elections():
    # Arrange
    load_accounts_from_dotenv()
    account = accounts[0]
    election_manager = ElectionManager.deploy({"from": account})

    # Act
    election_manager.createElection("E1", time(), {"from": account})
    election_manager.createElection("E2", time(), {"from": account})
    election_manager.createElection("E3", time(), {"from": account})
    election_manager.createElection("Rainbow Ponies", time(), {"from": account})

    # Assert
    electionNames = election_manager.getElectionNames()
    assert electionNames[0] == "E1"
    assert electionNames[1] == "E2"
    assert electionNames[2] == "E3"
    assert electionNames[3] == "Rainbow Ponies"
