import time
from turtle import width, window_width
import PySimpleGUI as sg
from black import err
from blockchain import *
from brownie import accounts
from datetime import datetime as dt
from dotenv import dotenv_values

# TODO: Implement help menus (ex: question marks that let you hover and click on then, could be used in "add account" section)
# TODO: Grey out buttons when you can't use them (ex: no eth, no candidates, already voted, etc)
# TODO: change vote bar at bottom to winner bar after election is over
# TODO: Put Election End Date beside title

# BUG: Displays won't get refreshed properly and program will crash if more than one instance is open at a time. Update: this seems to happen randomly. I don't know why. I think that it's PYSimpleGUI's fault.
# UPDATE #2: I think this is related to window.refresh() & forgetting to call it after making an update to the UI. Also seems to happen by calling it too often.

# BUG: after election list refresh, elections will get deslected


def build_ballot(candidates):
    ballot = []
    for candidate in candidates:
        ballot.append(
            [
                candidate.name,
                candidate.votes,
                candidate.address,
            ]
        )
    return ballot


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
                    "Your Balance: " + str(from_account.balance() / 10**18) + " ETH"
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


# Opens new window for adding account to the brownie accounts list
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
                    accounts.add(values["private_key"])
                    # append private key to PRIVATE_KEY variable in .env file
                    append_dotenv("PRIVATE_KEY", values["private_key"])
                    break
            except ValueError as e:
                window["account_error"].update(parse_error(str(e)), visible=True)

    window.close()


# Convert MM/DD/YYYY H:M:S Date to local Unix timestamp
def unix_time(MMDDYYYY):
    return int(dt.timestamp(dt.strptime(MMDDYYYY, "%m/%d/%Y %H:%M:%S")))


def refresh_election_list(election_list: sg.Listbox, manager_contract):
    election_list.update(get_elections(manager_contract))


def refresh_account_list(account_combo: sg.Combo, accounts):
    # 'value=accounts[-1]' makes sure that the selected account in the box is the one the user just added
    account_combo.update(values=accounts, value=accounts[-1])


def refresh_ballot(ballot: sg.Table, candidates):
    ballot.update(build_ballot(candidates))


# TODO: Fix error if environment variable does not already exist. Create variable, maybe?
def append_dotenv(env: str, to_append: str):
    envs = dotenv_values()
    envs[env] = envs[env] + "," + to_append
    with open(".env", "a") as file:
        file.truncate(0)
        for key in envs:
            file.write(f"{key}={envs[key]}\n")


# Get initial data from blockchain
elections = get_elections(MANAGER_CONTRACT)
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
initial_candidates = get_candidates(active_election)
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
        ),
        sg.Button("Admin Console", key="admin", button_color="#52accc", visible=False),
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
                        active_election.name if active_election is not None else "",
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
            size=(7, 1)
        ),  # Dummy spacer element to keep election title somewhat centered.
        sg.Button("⟳", key="refresh_ballot"),
    ],
    [
        sg.Table(
            build_ballot(get_candidates(active_election)),
            headings=["Candidate", "Votes", "Address"],
            key="ballot",
            expand_x=True,
            expand_y=True,
            # row_colors=("#ffffff", "#e3e5e8"),
            # alternating_row_color=False,
            justification="c",
            display_row_numbers=True,
        )
    ],
    [sg.HorizontalSeparator()],
    [
        sg.T("My vote:"),
        sg.Combo(
            initial_candidates,
            key="candidate_list",
            default_value=initial_candidates[0]
            if len(initial_candidates) > 0
            else None,
            enable_events=True,
            size=(15, 1),
        ),
        sg.Button("Vote", key="vote_button"),
        sg.Text("", key="vote_status", visible=False),
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
            values=elections,
            default_values=[elections[0]] if len(elections) > 0 else None,
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
window = sg.Window("Elections Canada", layout, icon="images/icon.ico", finalize=True)

# Setup objects
# Due to the limitations of PySimpleGUI, these objects can not be used to read the value of their own contents.
# To do that, you must use values["insert_object_key_here"]
# Ex: To read the currently selected account you would call values["account_list"]
account_list: sg.Combo = window["account_list"]
election_list: sg.Listbox = window["election_list"]
candidate_list: sg.Combo = window["candidate_list"]
ballot: sg.Table = window["ballot"]
election_title: sg.Text = window["election_title"]

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window
    if event == sg.WIN_CLOSED:
        break

    # Will be called anytime a event happens
    if event != "" and event != None:
        # Clear any temporary error/success messages
        window["vote_status"].update(visible=False)

    if event == "create_election":
        create_election_window(MANAGER_CONTRACT, values["account_list"])
        refresh_election_list(election_list, MANAGER_CONTRACT)

    if event == "add_account":
        add_account_window()
        refresh_account_list(account_list, accounts._accounts)
        # TODO: Show sentinel when account is added.

    if event == "refresh_elections":
        refresh_election_list(election_list, MANAGER_CONTRACT)

    if event == "election_list" and values["election_list"] != []:
        active_election = values["election_list"][0]
        candidates = get_candidates(active_election)
        candidate_list.update(
            values=candidates, value=candidates[0] if len(candidates) > 0 else None
        )
        election_title.update(value=active_election.name)
        refresh_ballot(ballot, candidates)

    if event == "vote_button":
        if values["candidate_list"] == "":
            sg.popup("Please select a candidate to vote for.", icon="images/icon.ico")
        else:
            window["vote_status"].update(
                "Submitting transaction...", visible=True, text_color="#52accc"
            )
            window.refresh()
            try:
                vote(
                    active_election,
                    values["candidate_list"].address,
                    values["account_list"],
                )
                candidates = get_candidates(active_election)
                refresh_ballot(ballot, candidates)
                window["vote_status"].update(
                    "Vote successful.", visible=True, text_color="#000000"
                )
                window.refresh()
            except ValueError as e:
                window["vote_status"].update(
                    parse_error(str(e)), visible=True, text_color="#860038"
                )
                window.refresh()

    if event == "run_for_office":
        if len(values["election_list"]) == 0:
            sg.popup(
                "Please select an election.",
                icon="images/icon.ico",
            )
        else:
            run_for_office_window(values["election_list"][0], values["account_list"])
            candidates = get_candidates(values["election_list"][0])
            refresh_ballot(ballot, candidates)
            candidate_list.update(
                values=candidates, value=candidates[0] if len(candidates) > 0 else None
            )

    if event == "refresh_ballot":
        if len(values["election_list"]) == 0:
            sg.popup(
                "Please select an election.",
                icon="images/icon.ico",
            )
        else:
            refresh_ballot(ballot, get_candidates(values["election_list"][0]))


window.close()