from generator.theme.base import BaseThemeGenerator
from generator.settings import SettingsManager


class PreviewThemeGenerator(BaseThemeGenerator):
    def __init__(self, manager: SettingsManager, render_factor: int):
        super().__init__(manager, render_factor)
