import PySimpleGUI as sg
from brownie import accounts, config, Election, ElectionManager, network
from deploy import deploy

election = deploy()

sg.Window(title="Elections Canada", layout=[[]], margins=(100, 50)).read()
