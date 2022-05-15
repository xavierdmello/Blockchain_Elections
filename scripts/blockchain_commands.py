from tkinter import NE
from brownie import Contract, accounts, config, network, project


def get_parsed_private_keys():
    return config["wallets"]["from_key"].split(",")


# Load brownie project
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


def get_election_list():
    return dict(
        zip(
            MANAGER_CONTRACT.getElections(),
            MANAGER_CONTRACT.getElectionNames(),
        )
    )


def create_election(election_name, election_end_time):
    return MANAGER_CONTRACT.createElection(
        election_name, election_end_time, {"from": active_account}
    )


def deploy_manager():
    return ElectionManager.deploy({"from": active_account})
