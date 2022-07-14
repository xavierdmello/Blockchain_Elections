import os
import PySimpleGUI as sg
import json
from datetime import datetime as dt
from dotenv import *
from genericpath import exists
from web3 import Web3


class WrappedElection:
    def __str__(self):
        return self.name

    def __init__(self, election_address: str, election_name: str):
        with open("abi/Election.json") as f:
            abi = json.load(f)
        self.contract = w3.eth.contract(address=election_address, abi=abi)
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
        self.ranks = []

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

        # Calculate rank of each Candidate.
        # Note that if two candidates have the same amount of votes, they are the same rank.
        for i, wrapped_candidate in enumerate(wrapped_candidates):
            # If the candidate is the first in the sorted list, it is rank 1
            if i == 0:
                self.ranks.append(1)
            else:
                # If the candidate has the same amount of votes as the one before it, it is the same rank
                if wrapped_candidate.votes == wrapped_candidates[i - 1].votes:
                    self.ranks.append(self.ranks[i - 1])
                else:
                    self.ranks.append(self.ranks[i - 1] + 1)


class Account:
    def __str__(self):
        return self.address

    # "name" parameter is optional and will be the address by default
    def __init__(self, private_key):
        self.private_key = private_key
        self.address = w3.eth.account.from_key(private_key).address


def get_elections(manager_contract, aggregator_contract):
    elections = []
    raw_election_bundles = aggregator_contract.functions.getElectionsBundledWithNames(
        manager_contract.address
    ).call()
    for raw_election_bundle in raw_election_bundles:
        elections.append(
            WrappedElection(raw_election_bundle[0], raw_election_bundle[1])
        )

    return elections


def get_balance(address):
    return w3.eth.get_balance(address)


def get_election_data(
    wrapped_election: WrappedElection, aggregator_contract
) -> ElectionData:
    return ElectionData(
        aggregator_contract.functions.getElectionData(
            wrapped_election.contract.address
        ).call()
    )


def create_election(manager_contract, election_name, election_end_time, from_account):
    if election_name is None or election_name == "":
        raise ValueError("Election name cannot be empty")

    w3.eth.wait_for_transaction_receipt(
        w3.eth.send_raw_transaction(
            w3.eth.account.sign_transaction(
                manager_contract.functions.createElection(
                    election_name, election_end_time
                ).buildTransaction(
                    {
                        "chainId": chain_id,
                        "from": from_account.address,
                        "nonce": w3.eth.get_transaction_count(from_account.address),
                        "gasPrice": w3.eth.gas_price,
                    }
                ),
                private_key=from_account.private_key,
            ).rawTransaction
        )
    )


def run_for_office(
    wrapped_election: WrappedElection, candidate_name: str, from_account: Account
):
    w3.eth.wait_for_transaction_receipt(
        w3.eth.send_raw_transaction(
            w3.eth.account.sign_transaction(
                wrapped_election.contract.functions.runForElection(
                    candidate_name
                ).buildTransaction(
                    {
                        "chainId": chain_id,
                        "from": from_account.address,
                        "nonce": w3.eth.get_transaction_count(from_account.address),
                        "gasPrice": w3.eth.gas_price,
                        "value": w3.toWei("0.05", "ether"),
                    }
                ),
                private_key=from_account.private_key,
            ).rawTransaction
        )
    )


def withdraw_revenue(wrapped_election: WrappedElection, from_account: Account):
    w3.eth.wait_for_transaction_receipt(
        w3.eth.send_raw_transaction(
            w3.eth.account.sign_transaction(
                wrapped_election.contract.functions.withdrawRevenue().buildTransaction(
                    {
                        "chainId": chain_id,
                        "from": from_account.address,
                        "nonce": w3.eth.get_transaction_count(from_account.address),
                        "gasPrice": w3.eth.gas_price,
                    }
                ),
                private_key=from_account.private_key,
            ).rawTransaction
        )
    )


def load_accounts_from_dotenv():
    accounts = []
    for private_key in get_parsed_private_keys():
        accounts.append(Account(private_key))
    return accounts


# Returns empty list if .env does not exist
def get_parsed_private_keys():
    if exists(".env"):
        return os.getenv("PRIVATE_KEY").split(",")
    else:
        return []


# Opens new window for creating election
# Returns True if election was created
def create_election_window(manager_contract, from_account):
    layout = (
        [
            [
                sg.Text("Create an election:"),
                sg.Push(),
                sg.Button("Back", key="back"),
            ],
            [sg.Text("Election Name:"), sg.In(key="election_name")],
            [
                sg.Text("Election End Date:"),
                sg.CalendarButton(
                    "Choose Date", target="in_date", format="%m/%d/%Y 23:59:59"
                ),
                sg.Text("", key="date_display_text"),
                sg.In(key="in_date", disabled=True, visible=False, enable_events=True),
            ],
            [
                sg.Button("Create Election", key="create_election_btn"),
                sg.Text(
                    "",
                    visible=False,
                    key="create_election_status",
                ),
            ],
        ],
    )
    window = sg.Window("Create Election", layout, icon="images/icon.ico", finalize=True)

    while True:
        event, values = window.read()
        if event == "back" or event == sg.WIN_CLOSED:
            break
        if event == "create_election_btn":
            window["create_election_status"].update(
                "Submitting transaction...", visible=True, text_color="#52accc"
            )
            window.refresh()
            try:
                create_election(
                    manager_contract,
                    values["election_name"],
                    unix_time(values["in_date"]),
                    from_account,
                )
                window.close()
                return True
            except ValueError as e:
                window["create_election_status"].update(
                    parse_error(str(e)),
                    visible=True,
                    text_color="#860038",
                )
        if event == "in_date":
            # Display selected date as election end time
            # Truncates time (end of the day) as it is not intended to be shown to the user
            window["date_display_text"].update(values["in_date"].split(" ")[0])
    window.close()


def parse_error(error: str) -> str:
    split_error = error.split(": '")

    # Gas estimation errors are thrown before a transaction is sent,
    # when brownie tries to decide how much of a transaction fee it needs to pay.
    # If there is an impossibility in the program (ex: trying to vote for someone when you have already voted),
    # brownie will throw an error, because it can't compute how to send the transaction.
    # The error has a lot of "boilerplate", and should be parsed before shown to the end-user.
    if len(split_error) > 1:
        error_msg = split_error[1].split("'")[0].capitalize()
        if "Execution reverted: " in error_msg:
            error_msg = error_msg.split("Execution reverted: ")[1].capitalize()
        return f"Error: {error_msg}"
    else:
        return f"Error: {error.capitalize()}"


def run_for_office_window(wrapped_election: WrappedElection, from_account):
    layout = (
        [
            [
                sg.Text("Run for office:"),
                sg.Push(),
                sg.Button("Back", key="back"),
            ],
            [sg.Text("Candidate Name:"), sg.In(key="candidate_name")],
            [
                sg.Text(
                    "Fee: "
                    + str(
                        wrapped_election.contract.functions.candidateFee().call()
                        / 10**18
                    )
                    + " ETH"
                )
            ],
            [
                sg.Text(
                    "Your Balance: "
                    + str(get_balance(from_account.address) / 10**18)
                    + " ETH"
                )
            ],
            [
                sg.Button("Run For Office", key="confirm_run_for_office"),
                sg.Text("", visible=False, key="run_for_office_status"),
            ],
        ],
    )
    window = sg.Window("Run For Office", layout, icon="images/icon.ico")

    while True:
        event, values = window.read()
        if event == "back" or event == sg.WIN_CLOSED:
            break
        if event == "confirm_run_for_office":
            window["run_for_office_status"].update(
                "Submitting transaction...", visible=True, text_color="#52accc"
            )
            window.refresh()
            try:
                run_for_office(wrapped_election, values["candidate_name"], from_account)
                break
            except ValueError as e:
                window["run_for_office_status"].update(
                    parse_error(str(e)), visible=True, text_color="#860038"
                )
                window.refresh()
    window.close()


# Opens new window for adding account to the brownie accounts list.
# Returns new account if it was added, None if it was not.
def add_account_window(accounts):
    layout = (
        [
            [
                sg.Text("Add an account:"),
                sg.Push(),
                sg.Button("Back", key="back"),
            ],
            [sg.Text("Private Key:"), sg.In(key="private_key")],
            [
                sg.Button("Add Account", key="add_account_btn"),
                sg.Text("", text_color="#860038", key="account_error", visible=False),
            ],
        ],
    )
    window = sg.Window("Add Account", layout, icon="images/icon.ico", finalize=True)

    while True:
        event, values = window.read()
        if event == "back" or event == sg.WIN_CLOSED:
            break
        if event == "add_account_btn":
            try:
                if values["private_key"] in get_parsed_private_keys():
                    window["account_error"].update(
                        "Error: Account already added", visible=True
                    )
                else:
                    accounts.append(Account(values["private_key"]))

                    # append private key to PRIVATE_KEY variable in .env file
                    append_dotenv("PRIVATE_KEY", values["private_key"])

                    window.close()
                    return Account(values["private_key"])
            except ValueError as e:
                window["account_error"].update(parse_error(str(e)), visible=True)

    window.close()


# Convert MM/DD/YYYY H:M:S date to local Unix timestamp
def unix_time(MMDDYYYY):
    return int(dt.timestamp(dt.strptime(MMDDYYYY, "%m/%d/%Y %H:%M:%S")))


# Convert unix timestamp to MM/DD/YYYY H:M date
def formatted_time(unix_time: int) -> str:
    return dt.fromtimestamp(unix_time).strftime("%m/%d/%Y, %H:%M")


# Returns election list
# Will deselect previously selected election
def refresh_election_list(window: sg.Window, manager_contract, aggregator_contract):
    wrapped_elections = get_elections(manager_contract, aggregator_contract)
    window["election_list"].update(
        values=wrapped_elections,
    )
    window.refresh()

    return wrapped_elections


def get_selected_election(window_values) -> WrappedElection:
    return (
        None
        if len(window_values["election_list"]) == 0
        else window_values["election_list"][0]
    )


def admin_console_window(wrapped_election: WrappedElection, from_account):
    layout = (
        [
            [
                sg.Text(
                    "Election Revenue: "
                    + str(get_balance(wrapped_election.contract.address) / 10**18)
                    + " ETH"
                ),
                sg.Push(),
                sg.Button("Back", key="back"),
            ],
            [
                sg.Button("Withdraw Revenue", key="withdraw_revenue_btn"),
                sg.Text(
                    "", text_color="#860038", key="admin_console_status", visible=False
                ),
            ],
        ],
    )
    window = sg.Window("Admin Console", layout, icon="images/icon.ico", finalize=True)

    while True:
        event, values = window.read()
        if event == "back" or event == sg.WIN_CLOSED:
            break
        if event == "withdraw_revenue_btn":
            window["admin_console_status"].update(
                "Submitting transaction...", visible=True, text_color="#52accc"
            )
            window.refresh()
            try:
                withdraw_revenue(wrapped_election, from_account)
                break
            except ValueError as e:
                window["admin_console_status"].update(parse_error(str(e)), visible=True)

    window.close()


def refresh_account_list(window: sg.Window, accounts, previously_selected_account=None):
    if len(accounts) != 0:
        if not previously_selected_account:
            window["account_list"].update(values=accounts, value=accounts[-1])
        else:
            # `value=previously_selected_account` makes sure that the selected account in the box is the one the user just added
            window["account_list"].update(
                values=accounts, value=previously_selected_account
            )
        window.refresh()


def vote(
    wrapped_election: WrappedElection,
    candidate_address,
    from_account,
    window,
    window_values,
    aggregator_contract,
):
    try:
        w3.eth.wait_for_transaction_receipt(
            w3.eth.send_raw_transaction(
                w3.eth.account.sign_transaction(
                    wrapped_election.contract.functions.vote(
                        candidate_address
                    ).buildTransaction(
                        {
                            "chainId": chain_id,
                            "from": from_account.address,
                            "nonce": w3.eth.get_transaction_count(from_account.address),
                            "gasPrice": w3.eth.gas_price,
                        }
                    ),
                    private_key=from_account.private_key,
                ).rawTransaction
            )
        )

        window["vote_blurb"].update(
            "Vote successful.", visible=True, text_color="#000000"
        )
        refresh_ballot(
            window,
            window_values["account_list"],
            get_selected_election(window_values),
            aggregator_contract,
        )
    except ValueError as e:
        window["vote_blurb"].update(
            parse_error(str(e)), visible=True, text_color="#860038"
        )
        window.refresh()


def refresh_ballot(
    window: sg.Window,
    active_account: Account,
    wrapped_election: WrappedElection,
    aggregator_contract,
):
    # wrapped_elections may be None if no election is currently selected in the UI.
    # Lots of effort has been taken to minimize this from happening, but there still are some edge cases.
    # This check is an easy way to handle them: if no elections are currently selected, the ballot doesn't get updated.
    if wrapped_election is not None:
        election_data = get_election_data(wrapped_election, aggregator_contract)

        # Update candidate list
        window["candidate_list"].update(
            values=election_data.wrapped_candidates,
            value=election_data.wrapped_candidates[0]
            if len(election_data.wrapped_candidates) > 0
            else None,
        )

        # Update title
        window["election_title"].update(value=election_data.election_name)

        # Enable election admin console if user is the election admin
        if active_account is not None and active_account != "" and active_account.address == election_data.owner:
            window["admin_console"].update(visible=True)
            # Hide vote spacer because the now visible admin console button will take up the space in its place.
            # Will be ever so slightly off center, due to the limitations of PySimpleGui not being made for dynamic layouts.
            window["vote_spacer"].update(visible=False)
        else:
            # Hide, then show refresh ballot button to make sure elements show up in the right order
            window["refresh_ballot"].update(visible=False)

            window["vote_spacer"].update(visible=True)
            window["admin_console"].update(visible=False)
            window["refresh_ballot"].update(visible=True)

        # Reset any potentially greyed out buttons (base case)
        window["run_for_office"].update(disabled=False)
        window["candidate_list"].update(disabled=False)
        window["vote_button"].update(disabled=False)
        window["vote_blurb"].update(
            "End: " + formatted_time(election_data.election_end_time),
            text_color="#000000",
            visible=True,
        )
        # Grey out button if user is already running for the election
        if (
            active_account == "" or active_account is None or active_account.address in election_data.candidate_addresses
        ):
            window["run_for_office"].update(disabled=True)
        # Grey out buttons if user has already voted
        if active_account is None or active_account == "":
            window["candidate_list"].update(disabled=True)
            window["vote_button"].update(disabled=True)
            window["vote_blurb"].update(
                f"Please add an account to vote.",
                text_color="#000000",
            )
        elif active_account.address in election_data.voters:
            window["candidate_list"].update(disabled=True)
            window["vote_button"].update(disabled=True)
            window["vote_blurb"].update(
                f"You have already voted.",
                text_color="#000000",
            )
        # Grey out buttons if election is ended
        if election_data.closed:
            window["run_for_office"].update(disabled=True)
            window["candidate_list"].update(disabled=True)
            window["vote_button"].update(disabled=True)
            window["vote_blurb"].update(
                f"Election ended on {formatted_time(election_data.election_end_time)}",
                text_color="#000000",
            )

        # Update ballot
        unwrapped_candidates = []
        for i, wrapped_candidate in enumerate(election_data.wrapped_candidates):
            unwrapped_candidates.append(
                [
                    election_data.ranks[i],
                    wrapped_candidate.name,
                    wrapped_candidate.votes,
                    wrapped_candidate.address,
                ]
            )
        window["ballot"].update(unwrapped_candidates)

        # Refresh window
        window.refresh()


def append_dotenv(env: str, to_append: str):
    if exists(".env"):
        envs = dotenv_values()
        envs[env] = envs[env] + "," + to_append
    else:
        envs = dict()
        envs[env] = to_append

    with open(".env", "a") as file:
        file.truncate(0)
        for key in envs:
            file.write(f"{key}={envs[key]}\n")


def main():
    # Load accounts from .env file
    accounts = load_accounts_from_dotenv()

    # Create theme
    sg.LOOK_AND_FEEL_TABLE["ElectionsCanadaTheme"] = {
        "BACKGROUND": "#FFFFFF",
        "TEXT": "#000000",
        "INPUT": "#bdc6b8",
        "TEXT_INPUT": "#860038",
        "SCROLL": "#860038",
        "BUTTON": ("#FFFFFF", "#860038"),
        "PROGRESS": ("#000000", "#000000"),
        "BORDER": 1,
        "SLIDER_DEPTH": 0,
        "PROGRESS_DEPTH": 0,
        "COLOR_LIST": ["#860038", "#bdc6b8", "#bce0da", "#ebf5ee"],
        "DESCRIPTION": ["Red", "Blue", "Grey", "Vintage", "Wedding"],
    }
    sg.theme("ElectionsCanadaTheme")

    # Candidates list of default selected election
    voting_col = [
        [sg.Column([[sg.Image(source="images/logo.png")]], justification="c")],
        [sg.HorizontalSeparator()],
        [
            sg.T("Logged in as:"),
            sg.Combo(
                accounts,
                key="account_list",
                default_value=accounts[0] if len(accounts) > 0 else None,
                enable_events=True,
                expand_x=True,
                readonly=True,
                size=(45, 1)
            ),
            sg.Button("Add Account", key="add_account"),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Button("Run For Office", key="run_for_office"),
            sg.Push(),
            sg.Column(
                [
                    [
                        sg.Text(
                            "",
                            key="election_title",
                            font=(
                                sg.DEFAULT_FONT[0],
                                11,
                                "underline",
                            ),
                        )
                    ]
                ],
                justification="c",
            ),
            sg.Push(),
            sg.T(
                size=(6, 1),
                key="vote_spacer",
            ),  # Dummy spacer element to keep election title somewhat centered.
            sg.Button(
                "Admin",
                key="admin_console",
                button_color="#52accc",
                visible=False,
            ),
            sg.Button("⟳", key="refresh_ballot"),
        ],
        [
            sg.Table(
                [],
                headings=["Rank", "Candidate", "Votes", "Address"],
                key="ballot",
                expand_y=True,
                expand_x=True,
                alternating_row_color="#e3e5e8", # Light Gray
                justification="c",
            )
        ],
        [sg.HorizontalSeparator()],
        # Default UI if election is closed or there are no elections (disable voting buttons etc.)
        [
            sg.T("My vote:", key="my_vote_text"),
            sg.Combo(
                [],
                key="candidate_list",
                enable_events=True,
                size=(15, 1),
                disabled=True,
                readonly=True
            ),
            sg.Button("Vote", key="vote_button", disabled=True),
            sg.Text(
                "",
                key="vote_blurb",
                text_color="#000000",
            ),
        ],
    ]

    elections_col = [
        [
            sg.Text("Choose an election:"),
            sg.Push(),
            sg.Button("Create Election", key="create_election"),
            sg.Button("⟳", key="refresh_elections"),
        ],
        [
            sg.Listbox(
                values=[],
                size=(40, 20),
                enable_events=True,
                key="election_list",
                background_color="#e3e5e8",
                text_color="#000000",
                highlight_background_color="#860038",
            )
        ],
    ]

    layout = [
        [
            sg.Column(voting_col, justification="c"),
            sg.VSeparator(),
            sg.Column(elections_col, key="elections_col"),
        ],
    ]

    # Create the window
    window = sg.Window(
        "Elections Canada",
        layout,
        icon="images/icon.ico",
        finalize=True,
    )

    # Load ABIs
    with open("abi/ElectionManager.json", "r") as f:
        election_manager_abi = json.load(f)
    with open("abi/ElectionDataAggregator.json", "r") as f:
        election_data_aggregator_abi = json.load(f)
    manager_contract = w3.eth.contract(
        address=MANAGER_CONTRACT_ADDRESS, abi=election_manager_abi
    )
    aggregator_contract = w3.eth.contract(
        address=AGGREGATOR_CONTRACT_ADDRESS, abi=election_data_aggregator_abi
    )

    # Populate the election list and select the first election by default
    wrapped_elections = refresh_election_list(window, manager_contract, aggregator_contract)
    if len(wrapped_elections) != 0:
        window["election_list"].update(set_to_index=0)
        refresh_ballot(
            window,
            accounts[0] if len(accounts) != 0 else None,
            wrapped_elections[0],
            aggregator_contract,
        )

    # Create an event loop
    first_loop = True
    while True:
        event, values = window.read()
        # End program if user closes window
        if event == sg.WIN_CLOSED:
            break

        if event == "create_election":
            if values["account_list"] == "" or values["account_list"] is None:
                sg.popup(
                    "Please add an account first.", icon="images/icon.ico"
                )
            else:
                no_previous_elections = len(window["election_list"].get_list_values()) == 0
                if not no_previous_elections:
                    # Store currently selected election
                    previously_selected_election_index = window.Element('election_list').Widget.curselection()[0]

                success = create_election_window(manager_contract, values["account_list"])

                # Will clear currently selected election
                wrapped_elections = refresh_election_list(window, manager_contract, aggregator_contract)

                if success:
                    # If new election was created, select it & refresh ballot
                    window["election_list"].update(set_to_index=len(wrapped_elections)-1)
                    refresh_ballot(
                        window,
                        values["account_list"],
                        wrapped_elections[-1],
                        aggregator_contract,
                    )
                elif not no_previous_elections:
                    # If election was not created, reselect the previously selected election
                    window["election_list"].update(set_to_index=previously_selected_election_index)

        if event == "add_account":
            previously_selected_account = values["account_list"]
            new_account = add_account_window(accounts)
            if new_account is None:
                # If no account was added
                refresh_account_list(
                    window,
                    accounts,
                    previously_selected_account=previously_selected_account,
                )
            else:
                refresh_account_list(window, accounts)
                refresh_ballot(
                    window,
                    new_account,
                    get_selected_election(values),
                    aggregator_contract,
                )

        if event == "refresh_elections":
            no_previous_elections = len(window["election_list"].get_list_values()) == 0
            if not no_previous_elections:
                # Store currently selected election
                previously_selected_election_index = window.Element('election_list').Widget.curselection()[0]

            # Will clear currently selected election
            refresh_election_list(window, manager_contract, aggregator_contract)

            if not no_previous_elections:
                # Set selected election back to the previously selected election
                window["election_list"].update(set_to_index=previously_selected_election_index)

        # If user selects a different election from the election list
        if event == "election_list" and get_selected_election(values) is not None:
            refresh_ballot(
                window,
                values["account_list"],
                get_selected_election(values),
                aggregator_contract,
            )

        if event == "vote_button":
            if values["candidate_list"] == "":
                sg.popup(
                    "Please select a candidate to vote for.", icon="images/icon.ico"
                )
            else:
                window["vote_blurb"].update(
                    "Submitting transaction...", visible=True, text_color="#52accc"
                )
                window.refresh()
                vote(
                    get_selected_election(values),
                    values["candidate_list"].address,
                    values["account_list"],
                    window,
                    values,
                    aggregator_contract,
                )

        if event == "run_for_office":
            if get_selected_election(values) is None:
                sg.popup(
                    "Please select an election.",
                    icon="images/icon.ico",
                )
            else:
                run_for_office_window(
                    get_selected_election(values), values["account_list"]
                )
                refresh_ballot(
                    window,
                    values["account_list"],
                    get_selected_election(values),
                    aggregator_contract,
                )

        if event == "refresh_ballot":
            if get_selected_election(values) is None:
                sg.popup(
                    "Please select an election.",
                    icon="images/icon.ico",
                )
            else:
                refresh_ballot(
                    window,
                    values["account_list"],
                    get_selected_election(values),
                    aggregator_contract,
                )

        if event == "account_list":
            if get_selected_election(values) is not None:
                refresh_ballot(
                    window,
                    values["account_list"],
                    get_selected_election(values),
                    aggregator_contract,
                )

        if event == "admin_console":
            if get_selected_election(values) is None:
                sg.popup(
                    "Please select an election.",
                    icon="images/icon.ico",
                )
            else:
                admin_console_window(
                    get_selected_election(values), values["account_list"]
                )

    window.close()


# Config
# Avalanche Testnet
RPC_PROVIDER = (
    "https://api.avax-test.network/ext/bc/C/rpc"
)
MANAGER_CONTRACT_ADDRESS = "0x52E993cCfB9b6af8C15CE98249837b76Df8e39F8"
AGGREGATOR_CONTRACT_ADDRESS = "0x030A0900270509502f836A41511306b7676C8a7A"

# Setup Web3
load_dotenv()
w3 = Web3(Web3.HTTPProvider(RPC_PROVIDER))
chain_id = w3.eth.chain_id

# Start GUI
main()
