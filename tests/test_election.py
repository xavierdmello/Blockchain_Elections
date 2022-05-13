import pytest
from brownie import Election, Wei, accounts
from scripts.blockchain_commands import get_account
from time import time, sleep


def test_get_candidate_name():
    account = get_account()
    address = account.address
    election = Election.deploy(
        address, "TestElection", time() + 99999999, {"from": account}
    )

    expected = "John Doe"
    election.runForElection(expected, {"from": account, "value": Wei("0.05 ether")})

    assert expected == election.candidateNames(address)


@pytest.mark.xfail
def test_time_close():
    account = get_account()
    address = account.address
    election = Election.deploy(address, "TestElection", time() + 2, {"from": account})

    sleep(3)
    election.runForElection(
        "TestCandidate", {"from": account, "value": Wei("0.05 ether")}
    )

    assert election.isCandidate(address) == True


@pytest.mark.xfail
def test_close():
    account = get_account()
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
    account = get_account()
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
    account = get_account()
    address = account.address
    election = Election.deploy(
        address, "TestElection", time() + 99999999, {"from": account}
    )

    election.runForElection(
        "TestCandidate", {"from": account, "value": Wei("0.05 ether")}
    )

    assert election.isCandidate(address) == True
