import flet as ft
from ankibot.ui import AnkibotApp

def main(page: ft.Page):
    AnkibotApp(page).start()

if __name__ == "__main__":
    ft.app(target=main)
