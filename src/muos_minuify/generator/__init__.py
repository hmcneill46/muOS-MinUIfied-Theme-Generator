from typing import Callable, Literal

from PIL import Image
from PIL.Image import Resampling

from ..settings import SettingsManager
from .components import Background, FooterGuides, HeaderBubbles, LauncherIcons


class ThemeGenerator:
    def __init__(
        self,
        manager: SettingsManager,
        render_factor: int = 5,
        on_progress: Callable | None = None,
    ):
        self.manager = manager
        self.render_factor = render_factor
        self.on_progress = on_progress

    @property
    def screen_dimensions(self) -> tuple[int, int]:
        return (
            int(self.manager.deviceScreenWidthVar),
            int(self.manager.deviceScreenHeightVar),
        )

    @property
    def scaled_screen_dimensions(self) -> tuple[int, int]:
        return (
            int(self.screen_dimensions[0] * self.render_factor),
            int(self.screen_dimensions[1] * self.render_factor),
        )

    def _generate_background(self) -> Image.Image:
        bg_hex = self.manager.bgHexVar
        use_background_image = self.manager.use_custom_background_var
        background_image_path = self.manager.background_image_path

        background = Background(
            manager=self.manager,
            screen_dimensions=self.screen_dimensions,
            render_factor=self.render_factor,
        ).with_background_hex(bg_hex)

        if use_background_image and background_image_path:
            background = background.with_background_image(background_image_path)

        background_image = background.generate(
            use_background_image=use_background_image
        )
        return background_image

    def _generate_header_bubbles(self) -> Image.Image:
        header_height = self.manager.headerHeightVar
        text_height = self.manager.header_text_height_var
        text_bubble_height = self.manager.header_text_bubble_height_var

        clock_format = self.manager.clock_format_var
        clock_bubble_alignment = self.manager.clock_alignment_var
        clock_bubble_margin_left = self.manager.clockHorizontalLeftPaddingVar
        clock_bubble_margin_right = self.manager.clockHorizontalRightPaddingVar

        status_bubble_alignment = self.manager.header_glyph_alignment_var
        status_glyph_height = self.manager.header_glyph_height_var
        status_bubble_height = self.manager.header_glyph_bubble_height_var
        status_bubble_padding_left = (
            self.manager.header_glyph_horizontal_left_padding_var
        )
        status_bubble_padding_right = (
            self.manager.header_glyph_horizontal_right_padding_var
        )

        header_bubbles = (
            HeaderBubbles(
                manager=self.manager,
                screen_dimensions=self.screen_dimensions,
                render_factor=self.render_factor,
            )
            .with_header_configuration(header_height, text_height, text_bubble_height)
            .with_clock_configuration(
                clock_format,
                clock_bubble_alignment,
                clock_bubble_margin_left,
                clock_bubble_margin_right,
            )
            .with_status_configuration(
                status_bubble_alignment,
                status_glyph_height,
                status_bubble_height,
                status_bubble_padding_left,
                status_bubble_padding_right,
            )
        )

        accent_colour = self.manager.deselectedFontHexVar
        show_clock_bubble = self.manager.show_clock_bubbles_var
        show_status_bubble = self.manager.show_glyphs_bubbles_var
        join_bubbles = self.manager.join_header_bubbles_var

        header_bubbles_image = header_bubbles.generate(
            accent_colour=accent_colour,
            show_clock_bubble=show_clock_bubble,
            show_status_bubble=show_status_bubble,
            join_bubbles=join_bubbles,
        )
        return header_bubbles_image

    def _generate_footer_guides(
        self, right_buttons: list[tuple[str, str]], left_buttons: list[tuple[str, str]]
    ) -> Image.Image:
        items_per_screen = self.manager.itemsPerScreenVar
        content_padding_top = self.manager.contentPaddingTopVar
        footer_ideal_height = self.manager.approxFooterHeightVar
        footer_margin_block = self.manager.VBG_Vertical_Padding_var
        footer_margin_inline = self.manager.VBG_Horizontal_Padding_var

        control_scheme = self.manager.muos_button_swap_var
        button_layout = self.manager.physical_controller_layout_var

        footer_guides = (
            FooterGuides(
                manager=self.manager,
                screen_dimensions=self.screen_dimensions,
                render_factor=self.render_factor,
            )
            .with_button_configuration(
                right_buttons,
                left_buttons,
                control_scheme,
                button_layout,
            )
            .with_footer_configuration(
                items_per_screen,
                content_padding_top,
                footer_ideal_height,
                footer_margin_block,
                footer_margin_inline,
            )
        )

        colour_hex = self.manager.footerBubbleHexVar
        show_left_guide = not self.manager.remove_left_menu_guides_var
        show_right_guide = not self.manager.remove_right_menu_guides_var

        footer_guides_image = footer_guides.generate(
            colour_hex,
            show_left_guide=show_left_guide,
            show_right_guide=show_right_guide,
        )
        return footer_guides_image

    def _generate_launcher_icons(
        self, launch_item: str, variant: Literal["Horizontal", "Alt-Horizontal"]
    ) -> Image.Image:
        selected_font_hex = self.manager.selectedFontHexVar
        deselected_font_hex = self.manager.deselectedFontHexVar
        bubble_hex = self.manager.bubbleHexVar
        icon_hex = self.manager.iconHexVar
        passthrough = self.manager.transparent_text_var

        launcher_icons = LauncherIcons(
            manager=self.manager,
            screen_dimensions=self.screen_dimensions,
            render_factor=self.render_factor,
        ).with_color_configuration(
            selected_font_hex=selected_font_hex,
            deselected_font_hex=deselected_font_hex,
            bubble_hex=bubble_hex,
            icon_hex=icon_hex,
        )

        launcher_icons_image = launcher_icons.generate(
            launch_item, variant, passthrough
        )
        return launcher_icons_image

    def generate_wall_image(
        self,
        right_buttons: list[tuple[str, str]],
        left_buttons: list[tuple[str, str]],
    ) -> Image.Image:
        image = self._generate_background()

        header_bubbles_image = self._generate_header_bubbles()
        image.alpha_composite(header_bubbles_image, (0, 0))

        footer_guides_image = self._generate_footer_guides(right_buttons, left_buttons)
        image.alpha_composite(footer_guides_image, (0, 0))

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def generate_static_image(
        self,
        right_buttons: list[tuple[str, str]],
        left_buttons: list[tuple[str, str]],
    ) -> Image.Image:
        image = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))

        header_bubbles_image = self._generate_header_bubbles()
        image.alpha_composite(header_bubbles_image)

        footer_guides_image = self._generate_footer_guides(right_buttons, left_buttons)
        image.alpha_composite(footer_guides_image)

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def generate_launcher_image(
        self,
        launch_item: str,
        right_buttons: list[tuple[str, str]],
        left_buttons: list[tuple[str, str]],
    ) -> Image.Image:
        if (variant := self.manager.main_menu_style_var) == "Vertical":
            return self.generate_static_image(right_buttons, left_buttons)

        image = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))

        launcher_icons_image = self._generate_launcher_icons(launch_item, variant)
        image.alpha_composite(launcher_icons_image)

        header_bubbles_image = self._generate_header_bubbles()
        image.alpha_composite(header_bubbles_image)

        footer_guides_image = self._generate_footer_guides(right_buttons, left_buttons)
        image.alpha_composite(footer_guides_image)

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def generate_theme(self):
        pass
        for _ in []:
            self.generate_wall_image()
            self.generate_static_image()

            if self.on_progress:
                self.on_progress()
