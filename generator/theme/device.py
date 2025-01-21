from generator.theme.base import BaseThemeGenerator
from generator.settings import SettingsManager


class DeviceThemeGenerator(BaseThemeGenerator):
    def __init__(self, manager: SettingsManager):
        super().__init__(manager, render_factor=1)
