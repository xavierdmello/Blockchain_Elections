from threading import Thread
import PySimpleGUI as sg
from scripts.blockchain import *
from brownie import accounts, network, ElectionManager, ElectionDataAggregator
from datetime import datetime as dt
from dotenv import dotenv_values

# TODO: Highlights for election winners and gold/silver/bronze medals for candidates.

# BUG: Displays won't get refreshed properly and program will crash if more than one instance is open at a time. Update: this seems to happen randomly. I don't know why. I think that it's PYSimpleGUI's fault.
# UPDATE #2: I think this is related to window.refresh() & forgetting to call it after making an update to the UI. Also seems to happen by calling it too often.

# BUG: after election list refresh, elections will get deslected


# Opens new window for creating election
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
                break
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
    # If there is an impossibility in the program (ex: trying to vote for someome when you have already voted),
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
                    + str(wrapped_election.contract.candidateFee() / 10**18)
                    + " ETH"
                )
            ],
            [
                sg.Text(
                    "Your Balance: "
                    + str(get_balance(from_account) / 10**18)
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


# Opens new window for adding account to the brownie accounts list. Returns new account if it was added, None if it was not.
def add_account_window():
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
                    # append private key to PRIVATE_KEY variable in .env file
                    append_dotenv("PRIVATE_KEY", values["private_key"])

                    window.close()
                    # TODO: Refresh button visiblity when new account added (currently only triggered by button switch)
                    return accounts.add(values["private_key"])
            except ValueError as e:
                window["account_error"].update(parse_error(str(e)), visible=True)

    window.close()


# Convert MM/DD/YYYY H:M:S date to local Unix timestamp
def unix_time(MMDDYYYY):
    return int(dt.timestamp(dt.strptime(MMDDYYYY, "%m/%d/%Y %H:%M:%S")))


# Convert unix timestamp to MM/DD/YYYY H:M date
def formatted_time(unix_time: int) -> str:
    return dt.fromtimestamp(unix_time).strftime("%m/%d/%Y, %H:%M")


def refresh_election_list(
    window: sg.Window, manager_contract: Contract, aggregator_contract: Contract
):
    window["election_list"].update(
        values=get_elections(manager_contract, aggregator_contract)
    )
    window.refresh()


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
                    + str(get_balance(wrapped_election.contract) / 10**18)
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


# Convert MM/DD/YYYY H:M:S date to local Unix timestamp
def unix_time(MMDDYYYY):
    return int(dt.timestamp(dt.strptime(MMDDYYYY, "%m/%d/%Y %H:%M:%S")))


# Convert unix timestamp to MM/DD/YYYY H:M date
def formatted_time(unix_time: int) -> str:
    return dt.fromtimestamp(unix_time).strftime("%m/%d/%Y, %H:%M")


def refresh_election_list(
    window: sg.Window, manager_contract: Contract, aggregator_contract: Contract
):
    window["election_list"].update(
        values=get_elections(manager_contract, aggregator_contract)
    )
    window.refresh()


# TODO: Note: this function may not be actually needed
def refresh_account_list(window: sg.Window, accounts, previously_selected_account=None):
    # `value=previously_selected_account` makes sure that the selected account in the box is the one the user just added
    if not previously_selected_account:
        window["account_list"].update(values=accounts._accounts, value=accounts[-1])
    else:
        window["account_list"].update(
            values=accounts._accounts, value=previously_selected_account
        )
    window.refresh()


def get_selected_election(window_values) -> WrappedElection:
    return (
        None
        if len(window_values["election_list"]) == 0
        else window_values["election_list"][0]
    )


def vote(
    wrapped_election: WrappedElection,
    candidate_address,
    from_account,
    window,
    window_values,
    aggregator_contract,
):
    try:
        tx = wrapped_election.contract.vote(candidate_address, {"from": from_account})
        tx.wait(1)
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
    active_account: str,
    wrapped_election: WrappedElection,
    aggregator_contract,
):
    thread = Thread(
        target=refresh_ballot1,
        args=(
            window,
            active_account,
            wrapped_election,
            aggregator_contract,
        ),
    )
    thread.start()


def refresh_ballot1(
    window: sg.Window,
    active_account: str,
    wrapped_election: WrappedElection,
    aggregator_contract: Contract,
):
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
    if active_account == election_data.owner:
        window["admin_console"].update(visible=True)
        # Hide vote spacer beacause the now visible admin console button will take up the space in it's place.
        # Will be ever so slightly off center, due to the limitations of PySimpleGui not being made for dyanmic layouts.
        window["vote_spacer"].update(visible=False)
    else:
        # Hide, then show refresh ballot button to make sure elements show up in the right order
        window["refresh_ballot"].update(visible=False)

        window["vote_spacer"].update(visible=True)
        window["admin_console"].update(visible=False)
        window["refresh_ballot"].update(visible=True)

    # Reset any potenitally greyed out buttons (base case)
    window["run_for_office"].update(disabled=False)
    window["candidate_list"].update(disabled=False)
    window["vote_button"].update(disabled=False)
    window["vote_blurb"].update(
        "End: " + formatted_time(election_data.election_end_time),
        text_color="#000000",
        visible=True,
    )
    # Grey out button if user is already running for the election
    if active_account in election_data.candidate_addresses:
        window["run_for_office"].update(disabled=True)
    # Grey out buttons if user has already voted
    if active_account in election_data.voters:
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
    for wrapped_candidate in election_data.wrapped_candidates:
        unwrapped_candidates.append(
            [wrapped_candidate.name, wrapped_candidate.votes, wrapped_candidate.address]
        )
    window["ballot"].update(unwrapped_candidates)

    # Refresh window
    window.refresh()


# TODO: Fix error if environment variable does not already exist. Create variable, maybe?
def append_dotenv(env: str, to_append: str):
    envs = dotenv_values()
    envs[env] = envs[env] + "," + to_append
    with open(".env", "a") as file:
        file.truncate(0)
        for key in envs:
            file.write(f"{key}={envs[key]}\n")


def main():
    # Load accounts from .env file
    load_accounts_from_dotenv()

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
        # TODO: Intergrate admin console
        [
            sg.T("Logged in as:"),
            sg.Combo(
                accounts._accounts,
                key="account_list",
                default_value=accounts._accounts[0]
                if len(accounts._accounts) > 0
                else None,
                enable_events=True,
                expand_x=True,
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
                size=(7, 1),
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
                headings=["Candidate", "Votes", "Address"],
                key="ballot",
                expand_y=True,
                expand_x=True,
                # row_colors=("#ffffff", "#e3e5e8"),
                # alternating_row_color=False,
                justification="c",
                display_row_numbers=True,
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

    # If set to True, new manager + aggregator contracts will be deployed.
    # However, these contracts won't be saved to the brownie config.
    DEPLOY_NEW_CONTRACTS = False

    if network.show_active() == "development" or DEPLOY_NEW_CONTRACTS:
        MANAGER_CONTRACT = ElectionManager.deploy({"from": accounts[0]})
        AGGREGATOR_CONTRACT = ElectionDataAggregator.deploy({"from": accounts[0]})
    else:
        MANAGER_CONTRACT = Contract.from_abi(
            "Election Manager",
            config["networks"][network.show_active()]["manager_contract"],
            ElectionManager.abi,
        )
        AGGREGATOR_CONTRACT = Contract.from_abi(
            "Election Data Aggregator",
            config["networks"][network.show_active()]["aggregator_contract"],
            ElectionDataAggregator.abi,
        )

    refresh_election_list(window, MANAGER_CONTRACT, AGGREGATOR_CONTRACT)

    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window
        if event == sg.WIN_CLOSED:
            break

        if event == "create_election":
            create_election_window(MANAGER_CONTRACT, values["account_list"])
            refresh_election_list(window, MANAGER_CONTRACT, AGGREGATOR_CONTRACT)

        if event == "add_account":
            previously_selected_account = values["account_list"]
            new_account = add_account_window()
            if new_account is None:
                # If no account was added
                refresh_account_list(
                    window,
                    accounts,
                    previously_selected_account=previously_selected_account,
                )
            else:
                refresh_account_list(window, accounts)
            # TODO: Show sentinel when account is added.

        if event == "refresh_elections":
            refresh_election_list(window, MANAGER_CONTRACT, AGGREGATOR_CONTRACT)

        # If user selects a different election from the election list
        if event == "election_list" and values["election_list"] != []:
            refresh_ballot(
                window,
                values["account_list"],
                get_selected_election(values),
                AGGREGATOR_CONTRACT,
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
                vote_thread = Thread(
                    target=vote,
                    args=(
                        get_selected_election(values),
                        values["candidate_list"].address,
                        values["account_list"],
                        window,
                        values,
                        AGGREGATOR_CONTRACT,
                    ),
                )
                vote_thread.start()

        if event == "run_for_office":
            if len(values["election_list"]) == 0:
                sg.popup(
                    "Please select an election.",
                    icon="images/icon.ico",
                )
            else:
                run_for_office_window(
                    values["election_list"][0], values["account_list"]
                )
                refresh_ballot(
                    window,
                    values["account_list"],
                    get_selected_election(values),
                    AGGREGATOR_CONTRACT,
                )

        if event == "refresh_ballot":
            if len(values["election_list"]) == 0:
                sg.popup(
                    "Please select an election.",
                    icon="images/icon.ico",
                )
            else:
                refresh_ballot(
                    window,
                    values["account_list"],
                    get_selected_election(values),
                    AGGREGATOR_CONTRACT,
                )
        # TODO: Modifiy so this condition changes less often
        if event == "account_list":
            refresh_ballot(
                window,
                values["account_list"],
                get_selected_election(values),
                AGGREGATOR_CONTRACT,
            )

        if event == "admin_console":
            if len(values["election_list"]) == 0:
                sg.popup(
                    "Please select an election.",
                    icon="images/icon.ico",
                )
            else:
                admin_console_window(
                    get_selected_election(values), values["account_list"]
                )

    window.close()
