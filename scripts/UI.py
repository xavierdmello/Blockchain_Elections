import PySimpleGUI as sg
from blockchain_commands import *
from brownie import accounts
from datetime import datetime as dt
from dotenv import dotenv_values

# Opens new window for creating election
def create_election_window():
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
            [sg.Button("Create Election", key="create_election_btn")],
        ],
    )
    window = sg.Window("Create Election", layout, icon="images/icon.ico", finalize=True)

    while True:
        event, values = window.read()
        if event == "back" or event == sg.WIN_CLOSED:
            break
        if event == "create_election_btn":
            create_election(
                MANAGER_CONTRACT, values["election_name"], unix_time(values["in_date"])
            )
            break
        if event == "in_date":
            # Display selected date as election end time
            # Truncates time (end of the day) as it is not intended to be shown to the user
            window["date_display_text"].update(values["in_date"].split(" ")[0])
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
            [sg.Button("Add Account", key="add_account_btn")],
        ],
    )
    window = sg.Window("Add Account", layout, icon="images/icon.ico", finalize=True)

    while True:
        event, values = window.read()
        if event == "back" or event == sg.WIN_CLOSED:
            break
        if event == "add_account_btn":
            accounts.add(values["private_key"])
            # append private key to PRIVATE_KEY variable in .env file
            append_dotenv("PRIVATE_KEY", values["private_key"])
            break
    window.close()


# Convert MM/DD/YYYY H:M:S Date to local Unix timestamp
def unix_time(MMDDYYYY):
    return int(dt.timestamp(dt.strptime(MMDDYYYY, "%m/%d/%Y %H:%M:%S")))


def refresh_election_list(manager_contract, window: sg.Window):
    window["election_list"].update(get_elections(MANAGER_CONTRACT))


def refresh_account_list(window: sg.Window):
    window["account_list"].update(accounts)


def refresh_ballot(window: sg.Window, election):
    window["election_table"].update(build_ballot(election))


# TODO: Fix error if environment variable does not already exist. Create variable, maybe?
def append_dotenv(env: str, to_append: str):
    envs = dotenv_values()
    envs[env] = envs[env] + "," + to_append
    with open(".env", "a") as file:
        file.truncate(0)
        for key in envs:
            file.write(f"{key}={envs[key]}\n")


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

voting_col = [
    [sg.Column([[sg.Image(source="images/logo.png")]], justification="c")],
    [sg.HorizontalSeparator()],
    # TODO: Intergrate admin console
    [
        sg.T("Logged in as:"),
        sg.Combo(
            accounts,
            key="account_list",
            default_value=accounts._accounts[0],
            enable_events=True,
        ),
        sg.Button("Admin Console", key="admin", button_color="#52accc", visible=False),
        sg.Button("Add Account", key="add_account"),
    ],
    [sg.HorizontalSeparator()],
    [sg.Text("", key="election_title")],
    [
        sg.Table(
            build_ballot(active_election),
            headings=["Candidate", "Votes", "Address"],
            key="election_table",
        )
    ],
    [sg.HorizontalSeparator()],
    [
        sg.T("My vote:"),
        sg.Combo(
            get_candidates(active_election),
            key="candidate_list",
            enable_events=True,
        ),
        sg.Button("Vote", key="vote_button"),
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
            values=get_elections(MANAGER_CONTRACT),
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


# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window
    if event == sg.WIN_CLOSED:
        break
    if event == "create_election":
        create_election_window()
        refresh_election_list(MANAGER_CONTRACT, window)
    if event == "add_account":
        add_account_window()
        refresh_account_list(window)
        # TODO: Show sentinel when account is added.
    if event == "refresh_elections":
        refresh_election_list(MANAGER_CONTRACT, window)
    if event == "account_list":
        active_account = values["account_list"]
    if event == "election_list" and values["election_list"] != []:
        active_election = values["election_list"][0]
        window["candidate_list"].update(value=get_candidates(active_election))
        refresh_ballot(window, active_election)
    if event == "vote_button":
        vote(active_election, values["candidate_list"])
        refresh_ballot(window, active_election)


window.close()
