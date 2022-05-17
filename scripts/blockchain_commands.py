from brownie import (
    Contract,
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
    return manager_contract.createElection(
        election_name, election_end_time, {"from": from_account}
    )


def deploy_manager(from_account):
    return ElectionManager.deploy({"from": from_account})


def get_candidate_name(election, candidate_address: str) -> str:
    return election.candidateNames(candidate_address)


def get_num_votes(election, candidate_address: str) -> int:
    return election.getNumVotes(candidate_address)


def vote(election, candidate_address, from_account):
    election.vote(candidate_address, {"from": from_account})


def get_election_names(manager_contract):
    return manager_contract.getElectionNames()


def get_candidates(election):
    candidates = []
    if election == None:
        return candidates

    candidate_addresses = election.contract.getCandidates()
    for candidate_address in candidate_addresses:
        candidates.append(
            WrappedCandidate(
                candidate_address,
                get_candidate_name(candidate_address),
                get_num_votes(candidate_address),
            )
        )
    return candidates


# Load brownie project
# TODO: Fix project not loading without .env file. Create one maybe?
p = project.load(name="ElectionsCanada")
p.load_config()
from brownie.project.ElectionsCanada import *

# Election Manager Contract & Network
NETWORK = "rinkeby"
network.main.connect(NETWORK)
MANAGER_CONTRACT = Contract.from_abi(
    "ElectionManager",
    "0x8769D96Fd61226E536C751bE95dE65DF14D419bf",
    ElectionManager.abi,
)


# Load accounts & election
for private_key in get_parsed_private_keys():
    accounts.add(private_key)
elections = get_elections(MANAGER_CONTRACT)
if len(elections) == 0:
    active_election = None
else:
    active_election = elections[0]
