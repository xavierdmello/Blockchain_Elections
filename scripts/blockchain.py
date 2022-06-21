from brownie import (
    Contract,
    Wei,
    accounts,
    config,
    Election,
    ElectionManager,
    ElectionDataAggregator,
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

    def __init__(self, votes: int, candidate_name: str, candidate_address: str):
        self.address = candidate_address
        self.name = candidate_name
        self.votes = votes


class ElectionData:
    def __init__(self, raw_election_data):
        self.election_name = raw_election_data[0]
        self.voters = set(raw_election_data[1])
        self.owner = raw_election_data[3]
        self.candidate_fee = raw_election_data[4]
        self.election_end_time = raw_election_data[5]
        self.election_start_time = raw_election_data[6]
        self.closed = raw_election_data[7]

        raw_candidates = raw_election_data[2]
        wrapped_candidates = []
        candidate_addresses = []
        for raw_candidate in raw_candidates:
            wrapped_candidates.append(
                WrappedCandidate(raw_candidate[0], raw_candidate[1], raw_candidate[2])
            )
            candidate_addresses.append(raw_candidate[2])
        # Sort wrapped candidates by votes
        self.wrapped_candidates = sorted(
            wrapped_candidates,
            key=lambda wrapped_candidate: wrapped_candidate.votes,
            reverse=True,
        )
        self.candidate_addresses = set(candidate_addresses)


def get_parsed_private_keys():
    return config["wallets"]["from_key"].split(",")


def get_elections(manager_contract: Contract, aggregator_contract: Contract):
    elections = []
    raw_election_bundles = aggregator_contract.getElectionsBundledWithNames(
        manager_contract
    )
    for raw_election_bundle in raw_election_bundles:
        elections.append(
            WrappedElection(raw_election_bundle[0], raw_election_bundle[1])
        )

    return elections


def get_balance(address):
    return address.balance()


def get_election_data(
    wrapped_election: WrappedElection, aggregator_contract: Contract
) -> ElectionData:
    return ElectionData(aggregator_contract.getElectionData(wrapped_election.contract))


def create_election(manager_contract, election_name, election_end_time, from_account):
    if election_name == None or election_name == "":
        raise ValueError("Election name cannot be empty")
    tx = manager_contract.createElection(
        election_name, election_end_time, {"from": from_account}
    )
    tx.wait(1)


def deploy_manager(from_account):
    return ElectionManager.deploy({"from": from_account})


def run_for_office(
    wrapped_election: WrappedElection, candidate_name: str, from_account: str
):
    tx = wrapped_election.contract.runForElection(
        candidate_name, {"from": from_account, "value": Wei("0.05 ether")}
    )
    tx.wait(1)


def withdraw_revenue(wrapped_election: WrappedElection, from_account: str):
    tx = wrapped_election.contract.withdrawRevenue({"from": from_account})
    tx.wait(1)


def load_accounts_from_dotenv():
    for private_key in get_parsed_private_keys():
        accounts.add(private_key)
