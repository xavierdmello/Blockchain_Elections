from cgitb import text
from tkinter import CENTER
import PySimpleGUI as sg
from blockchain_commands import get_account

sg.theme("LightBrown13")
elections_col = [
    [sg.Text("Elections")],
    [sg.Listbox(values=[], size=(40, 20), enable_events=True)],
]
voting_col = [
    [sg.Image(source="images/logo.png")],
    [sg.HorizontalSeparator()],
    [sg.Button("Switch Account")],
    [sg.Text(size=(40, 17), key="-TOUT-")],
]
accounts_col = [
    [sg.Text("Accounts")],
    [sg.Listbox(values=[], size=(40, 20), enable_events=True)],
]

layout = [
    [
        sg.Column(elections_col),
        sg.VSeparator(),
        sg.Column(voting_col, element_justification="center"),
        sg.VSeparator(),
        sg.Column(accounts_col),
    ]
]
# Create the window
window = sg.Window("Elections Canada", layout)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()
