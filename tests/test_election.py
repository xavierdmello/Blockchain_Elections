import pytest
from brownie import Election, Wei, accounts
from scripts.blockchain import load_accounts_from_dotenv
from time import time, sleep


def test_get_candidate_name():
    # Arrange
    load_accounts_from_dotenv()
    account = accounts[0]
    election = Election.deploy(
        account, "TestElection", time() + 99999999, {"from": account}
    )

    # Act
    expected = "John Doe"
    election.runForElection(expected, {"from": account, "value": Wei("0.05 ether")})

    # Assert
    assert expected == election.candidateNames(account)


@pytest.mark.xfail
def test_time_close():
    # Arrange
    account = accounts[0]
    address = account.address
    election = Election.deploy(address, "TestElection", time() + 2, {"from": account})

    # Act
    sleep(3)
    election.runForElection(
        "TestCandidate", {"from": account, "value": Wei("0.05 ether")}
    )

    # Assert
    assert election.isCandidate(address) == True


@pytest.mark.xfail
def test_close():
    load_accounts_from_dotenv()
    account = accounts[0]
    address = account.address
    election = Election.deploy(
        address, "TestElection", time() + 99999999, {"from": account}
    )

    election.close({"from": account})
    election.runForElection(
        "TestCandidate", {"from": account, "value": Wei("0.05 ether")}
    )

    assert election.isCandidate(address) == True


def test_vote():
    load_accounts_from_dotenv()
    account = accounts[0]
    address = account.address
    election = Election.deploy(
        address, "TestElection", time() + 99999999, {"from": account}
    )
    election.runForElection(
        "TestCandidate", {"from": account, "value": Wei("0.05 ether")}
    )

    election.vote(address, {"from": account})

    assert election.getNumVotes(address) == 1


def test_run_for_election():
    load_accounts_from_dotenv()
    account = accounts[0]
    address = account.address
    election = Election.deploy(
        address, "TestElection", time() + 99999999, {"from": account}
    )

    election.runForElection(
        "TestCandidate", {"from": account, "value": Wei("0.05 ether")}
    )

    assert election.isCandidate(address) == True
