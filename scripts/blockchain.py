from datetime import datetime
from tkinter import E
from brownie import (
    Contract,
    Wei,
    accounts,
    config,
    network,
    project,
)


class WrappedElection:
    def __str__(self):
        return self.name

    def __init__(self, election_address: str, election_name: str):
        self.contract = Contract.from_abi("Election", election_address, Election.abi)
        self.name = election_name


class WrappedCandidate:
    def __str__(self):
        return self.name

    def __init__(self, candidate_address: str, candidate_name: str, votes: int):
        self.address = candidate_address
        self.name = candidate_name
        self.votes = votes


def get_parsed_private_keys():
    return config["wallets"]["from_key"].split(",")


def get_elections(manager_contract: Contract):
    elections = []
    election_addresses = manager_contract.getElections()
    election_names = get_election_names(manager_contract)

    for election_address, election_name in zip(election_addresses, election_names):
        elections.append(WrappedElection(election_address, election_name))
    return elections


def create_election(manager_contract, election_name, election_end_time, from_account):
    if election_name == None or election_name == "":
        raise ValueError("Election name cannot be empty")
    tx = manager_contract.createElection(
        election_name, election_end_time, {"from": from_account}
    )
    tx.wait(1)


def is_closed(wrapped_election: WrappedElection):
    return wrapped_election.contract.isClosed()


def deploy_manager(from_account):
    return ElectionManager.deploy({"from": from_account})


def get_candidate_name(
    wrapped_election: WrappedElection, candidate_address: str
) -> str:
    return wrapped_election.contract.candidateNames(candidate_address)


def get_num_votes(wrapped_election: WrappedElection, candidate_address: str) -> int:
    return wrapped_election.contract.getNumVotes(candidate_address)


def vote(wrapped_election: WrappedElection, candidate_address, from_account):
    tx = wrapped_election.contract.vote(candidate_address, {"from": from_account})
    tx.wait(1)


def run_for_office(
    wrapped_election: WrappedElection, candidate_name: str, from_account: str
):
    tx = wrapped_election.contract.runForElection(
        candidate_name, {"from": from_account, "value": Wei("0.05 ether")}
    )
    tx.wait(1)


def get_winners(wrapped_election: WrappedElection):
    return wrapped_election.contract.getHighestVotes()


def get_election_names(manager_contract):
    return manager_contract.getElectionNames()


def get_candidates(wrapped_election: WrappedElection):
    candidates = []
    if wrapped_election == None:
        return candidates

    candidate_addresses = wrapped_election.contract.getCandidates()
    for candidate_address in candidate_addresses:
        candidates.append(
            WrappedCandidate(
                candidate_address,
                get_candidate_name(wrapped_election, candidate_address),
                get_num_votes(wrapped_election, candidate_address),
            )
        )
    return candidates


def get_end_time(wrapped_election: WrappedElection):
    end_time = wrapped_election.contract.electionEndTime()
    return datetime.fromtimestamp(end_time).strftime("%m/%d/%Y, %H:%M")


# Load brownie project
# TODO: Fix project not loading without .env file. Create one maybe?
p = project.load(name="ElectionsCanada")
p.load_config()
from brownie.project.ElectionsCanada import *

# Election Manager Contract & Network
NETWORK = "ftm-test"
network.main.connect(NETWORK)

# Load accounts & election
for private_key in get_parsed_private_keys():
    accounts.add(private_key)
MANAGER_CONTRACT = Contract.from_abi(
    "Election Manager",
    config["networks"][network.show_active()]["manager_contract"],
    ElectionManager.abi,
)
elections = get_elections(MANAGER_CONTRACT)
if len(elections) == 0:
    active_election = None
else:
    active_election = elections[0]
