import re
from webbrowser import get
from brownie import Contract, accounts, config, network, project


def get_parsed_private_keys():
    return config["wallets"]["from_key"].split(",")


def wrap_election(election_address: str):
    return Contract.from_abi("Election", election_address, Election.abi)


def get_elections(manager_contract: Contract):
    elections = []
    for election in manager_contract.getElections():
        elections.append(wrap_election(election))
    return elections


def create_election(manager_contract, election_name, election_end_time):
    return manager_contract.createElection(
        election_name, election_end_time, {"from": active_account}
    )


def deploy_manager():
    return ElectionManager.deploy({"from": active_account})


def get_candidates(election) -> list:
    return election.getCandidates()


def get_candidate_name(election, candidate_address: str) -> str:
    return election.candidateNames(candidate_address)


def get_num_votes(election, candidate_address: str) -> int:
    return election.getNumVotes(candidate_address)


def build_ballot(election):
    ballot = []
    for candidate in get_candidates(election):
        ballot.append(
            [
                get_candidate_name(election, candidate),
                get_num_votes(election, candidate),
                candidate,
            ]
        )
    return ballot


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
    "0x4f65f5bDcd4cbf861730f1A5127365FAc6121eEF",
    ElectionManager.abi,
)

# Load accounts
for private_key in get_parsed_private_keys():
    accounts.add(private_key)
active_account = accounts[0]
active_election = get_elections(MANAGER_CONTRACT)[0]
