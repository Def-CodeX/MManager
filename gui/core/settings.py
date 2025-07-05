import json


class Settings:
    def __init__(self):
        try:
            with open("gui/core/settings.json", 'r') as f:
                settings: dict = json.load(f)
        except FileNotFoundError:
            settings = {
                "theme": {
                    "name": "",
                    "colors": dict(),
                    "font": dict(),
                    "icons": dict()
                }
            }

        self.theme = settings.get('theme')
