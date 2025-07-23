import json


class Settings:
    def __init__(self):
        try:
            with open("gui/core/settings.json", 'r') as f:
                settings: dict = json.load(f)
        except FileNotFoundError:
            settings = {
                "theme": {
                    "DefCodeX Dark": {
                        "colors": dict(),
                        "font": dict(),
                        "icons": dict()
                    }
                }
            }

        self.theme = settings.get('theme')

    def get_theme(self, theme_name: str = "DefCodeX Dark"):
        return self.theme.get(theme_name)
