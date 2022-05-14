from cgitb import text
from tkinter import CENTER
import PySimpleGUI as sg
from blockchain_commands import get_election_list

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
top_bar = [[sg.Push(), sg.Button("-", key="minimize"), sg.Button("x", key="exit")]]
elections_col = [
    [
        sg.Text("Choose an election:"),
        sg.Push(),
        sg.Button("Create Election", key="-CREATE ELECTION-"),
        sg.Button("⟳", key="-REFRESH-"),
    ],
    [
        sg.Listbox(
            values=get_election_list().values(),
            size=(40, 20),
            enable_events=True,
            key="-ELECTION LIST-",
            background_color="#f2f3f5",
            text_color="#000000",
            highlight_background_color="#860038",
        )
    ],
]
voting_col = [
    [sg.Image(source="images/logo.png")],
    [sg.HorizontalSeparator()],
    [sg.Button("Switch Account")],
]
accounts_col = [
    [sg.Text("Choose An Account:")],
    [sg.Listbox(values=[], size=(40, 20), enable_events=True, key="-ACCOUNT LIST-")],
]
create_election_col = [
    [sg.Text("Election Name:"), sg.In(key="-ELECTION NAME-")],
    [
        sg.Text("Election End Date:"),
        sg.CalendarButton("Choose Date", target=(1, 0), key="date"),
    ],
]

layout = [
    [
        sg.Titlebar(
            "",
            "images/icon.png",
            background_color="#e3e5e8",
            text_color="#5e6976",
            font="Bold",
        )
    ],
    [
        sg.Column(voting_col, element_justification="center"),
        sg.VSeparator(),
        sg.Column(elections_col),
    ],
]
# Create the window
window = sg.Window(
    "Elections Canada",
    layout,
    no_titlebar=True,
    keep_on_top=True,
    finalize=True,
    resizable=True,
)
# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED or event == "exit":
        break
    if event == "-CREATE ELECTION-":
        layout[0].pop(len(layout[0]) - 1)
        layout[0].append(create_election_col)
    if event == "minimize":
        window.close()


window.close()
