import PySimpleGUI as sg
from hypothesis import target
from blockchain_commands import get_election_list, create_election
from brownie import accounts
from datetime import datetime as dt

# Open in new window
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
            create_election(values["election_name"], unix_time(values["in_date"]))
            break
        if event == "in_date":
            # Display selected date as election end time
            # Truncates time (end of the day) as it is not intended to be shown to the user
            window["date_display_text"].update(values["in_date"].split(" ")[0])
    window.close()


# Convert MM/DD/YYYY H:M:S Date to local Unix timestamp
def unix_time(MMDDYYYY):
    return int(dt.timestamp(dt.strptime(MMDDYYYY, "%m/%d/%Y %H:%M:%S")))


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
    [sg.T(size=(40, 15))],
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
            values=get_election_list().values(),
            size=(40, 20),
            enable_events=True,
            key="election_list",
            background_color="#e3e5e8",
            text_color="#000000",
            highlight_background_color="#860038",
        )
    ],
]

accounts_col = [
    [
        sg.Text("Choose an account:"),
        sg.Push(),
        sg.Button("Add Account", key="add_account"),
    ],
    [
        sg.Listbox(
            values=accounts,
            size=(40, 20),
            enable_events=True,
            key="account_list",
            background_color="#e3e5e8",
            text_color="#000000",
            highlight_background_color="#860038",
        )
    ],
]

layout = [
    [
        sg.Column(voting_col),
        sg.VSeparator(),
        sg.Column(elections_col, key="elections_col"),
        sg.VSeparator(),
        sg.Column(accounts_col, key="accounts_col"),
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
    if event == "add_account":
        pass
    if event == "refresh_elections":
        window["election_list"].update(get_election_list().values())

window.close()
