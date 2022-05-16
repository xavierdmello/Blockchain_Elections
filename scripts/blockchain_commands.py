from brownie import Contract, accounts, config, network, project


class WrappedElection(Contract):
    def __str__(self):
        return self.name

    def __init__(self, election_address):
        super().__init__(election_address)
        self.name = self.electionName()


# Wraps address into a special Election contract that returns its name when read as a string
def wrap_election(election_address: str):

    # election = Contract.from_abi("Election", election_address, Election.abi)
    # election.name = (
    #     election.electionName()
    # )  # Trick to make electionName() required to be called only once

    # def new__str__(self):
    #     return self.name

    # election.super().__str__ = types.MethodType(new__str__, election)
    # return election

    # return Contract.from_abi("Election", election_address, Election.abi)
    return WrappedElection(election_address)


def get_parsed_private_keys():
    return config["wallets"]["from_key"].split(",")


def get_elections(manager_contract: Contract):
    elections = []
    for election_address in manager_contract.getElections():
        elections.append(wrap_election(election_address))
    return elections


def create_election(manager_contract, election_name, election_end_time):
    return manager_contract.createElection(
        election_name, election_end_time, {"from": active_account}
    )


def deploy_manager():
    return ElectionManager.deploy({"from": active_account})


def get_candidates(election) -> list:
    if election == None:
        return []
    return election.getCandidates()


def get_candidate_name(election, candidate_address: str) -> str:
    return election.candidateNames(candidate_address)


def get_num_votes(election, candidate_address: str) -> int:
    return election.getNumVotes(candidate_address)


def vote(election, candidate_address):
    election.vote(candidate_address, {"from": active_account})


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
# MANAGER_CONTRACT = Contract.from_abi(
#     "ElectionManager",
#     "0x8769D96Fd61226E536C751bE95dE65DF14D419bf",
#     ElectionManager.abi,
# )
MANAGER_CONTRACT = Contract("0x8769D96Fd61226E536C751bE95dE65DF14D419bf")
print(MANAGER_CONTRACT._name)

# Load accounts & election
for private_key in get_parsed_private_keys():
    accounts.add(private_key)
active_account = accounts[0]
elections = get_elections(MANAGER_CONTRACT)
if len(elections) == 0:
    active_election = None
else:
    active_election = elections[0]

a = WrappedElection("0xECEFA8E04BDA2E2BE37FB3E5680EE194A297916E")

b = Contract("0xECEFA8E04BDA2E2BE37FB3E5680EE194A297916E")
print(a._name)
print(b._name)
