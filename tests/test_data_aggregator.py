from brownie import (
    Contract,
    ElectionManager,
    accounts,
    ElectionDataAggregator,
    Election,
)
from scripts.blockchain import ElectionData, load_accounts_from_dotenv
from time import time


def test_deploy_aggregator():
    # Arrange
    load_accounts_from_dotenv()
    account = accounts[0]

    # Act
    aggregator = ElectionDataAggregator.deploy({"from": account})

    # Assert
    assert aggregator.address != None


def test_get_elections_bundled_with_names():
    # Arrange
    load_accounts_from_dotenv()
    account = accounts[0]
    aggregator = ElectionDataAggregator.deploy({"from": account})
    election_manager = ElectionManager.deploy({"from": account})
    election_manager.createElection("E1", time(), {"from": account})
    election_manager.createElection("E2", time(), {"from": account})
    election_manager.createElection("E3", time(), {"from": account})

    # Act
    elections = aggregator.getElectionsBundledWithNames(election_manager)

    # Assert
    assert elections[0][1] == "E1"
    assert elections[1][1] == "E2"
    assert elections[2][1] == "E3"


def test_get_election_data():
    # Arrange
    load_accounts_from_dotenv()
    account = accounts[0]
    aggregator = ElectionDataAggregator.deploy({"from": account})
    election_manager = ElectionManager.deploy({"from": account})

    ELECTION_NAME = "USA"
    ELECTION_END_TIME = time() + 1000
    election = election_manager.createElection(
        ELECTION_NAME, ELECTION_END_TIME, {"from": account}
    ).return_value

    # Act
    election_data = ElectionData(aggregator.getElectionData(election))

    # Assert
    assert election_data.closed == False
    assert election_data.election_name == ELECTION_NAME
    assert election_data.election_end_time == ELECTION_END_TIME

    # Testing change of data by closing election
    # Arrange
    election_contract = Contract.from_abi("Election", election, Election.abi)
    election_contract.close({"from": account})

    # Act
    election_data = ElectionData(aggregator.getElectionData(election))

    # Assert
    assert election_data.closed == True
