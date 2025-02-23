from pathlib import Path
import shutil
from typing import Callable, Literal

from PIL import Image
from PIL.Image import Resampling

from ..constants import (
    SYSTEM_LOGOS_SCRIPT_PATH,
    THEME_SHELL_DIR,
    OVERLAY_DIR,
    MENU_DEFINITIONS_PATH,
    GLYPHS_DIR,
    SYSTEM_LOGOS_DIR,
    BatteryStyleOptionsDict,
    BatteryChargingStyleOptionsDict,
)
from ..utils import copy_contents, ensure_folder_exists, read_json, delete_folder
from ..color_utils import change_logo_color
from ..defaults import DEFAULT_FONT_PATH
from ..settings import SettingsManager
from ..scheme import SchemeRenderer
from .components import (
    Background,
    BootScreen,
    FooterGuides,
    HeaderBubbles,
    LauncherIcons,
)
from .components.font import HasFont


class ThemeGenerator(HasFont):
    def __init__(
        self,
        manager: SettingsManager,
        render_factor: int = 5,
        renderer: SchemeRenderer | None = None,
        font_path: Path = DEFAULT_FONT_PATH,
    ):
        super().__init__(font_path=font_path)
        self.manager = manager
        self.render_factor = render_factor
        self.renderer = renderer

        kwargs = {
            "manager": self.manager,
            "screen_dimensions": self.screen_dimensions,
            "render_factor": self.render_factor,
        }

        self.background = Background(**kwargs)
        self.header_bubbles = HeaderBubbles(**kwargs)
        self.footer_guides = FooterGuides(**kwargs)
        self.launcher_icons = LauncherIcons(**kwargs)

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

        background = self.background.with_background_hex(bg_hex)

        if use_background_image and background_image_path:
            background = background.with_background_image(background_image_path)

        background_image = background.generate(
            use_background_image=use_background_image
        )
        return background_image

    def _generate_header_bubbles(self, *args) -> Image.Image:
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

        header_bubbles = self.header_bubbles

        header_bubbles = (
            header_bubbles.with_header_configuration(
                header_height, text_height, text_bubble_height
            )
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

        footer_guides = self.footer_guides

        footer_guides = footer_guides.with_button_configuration(
            right_buttons,
            left_buttons,
            control_scheme,
            button_layout,
        ).with_footer_configuration(
            items_per_screen,
            content_padding_top,
            footer_ideal_height,
            footer_margin_block,
            footer_margin_inline,
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

        launcher_icons = self.launcher_icons

        launcher_icons = launcher_icons.with_color_configuration(
            selected_font_hex=selected_font_hex,
            deselected_font_hex=deselected_font_hex,
            bubble_hex=bubble_hex,
            icon_hex=icon_hex,
        )

        launcher_icons_image = launcher_icons.generate(
            launch_item, variant, passthrough
        )
        return launcher_icons_image

    def _generate_boot_logo_image(self) -> Image.Image:
        bg_hex = self.manager.bgHexVar
        deselected_font_hex = self.manager.deselectedFontHexVar
        bubble_hex = self.manager.bubbleHexVar
        icon_hex = self.manager.iconHexVar

        boot_screen = BootScreen(
            manager=self.manager,
            screen_dimensions=self.screen_dimensions,
            render_factor=self.render_factor,
        ).with_color_configuration(
            bg_hex=bg_hex,
            deselected_font_hex=deselected_font_hex,
            bubble_hex=bubble_hex,
            icon_hex=icon_hex,
        )

        if use_custom_logo := self.manager.use_custom_bootlogo_var:
            boot_screen = boot_screen.with_bootlogo_image(
                self.manager.bootlogo_image_path
            )

        bootlogo_image = boot_screen.generate_with_logo(use_custom_logo)
        return bootlogo_image

    def _generate_boot_text_image(
        self, display_text: str, icon_path: Path | None = None
    ) -> Image.Image:
        bg_hex = self.manager.bgHexVar
        deselected_font_hex = self.manager.deselectedFontHexVar
        bubble_hex = self.manager.bubbleHexVar
        icon_hex = self.manager.iconHexVar

        boot_screen = BootScreen(
            manager=self.manager,
            screen_dimensions=self.screen_dimensions,
            render_factor=self.render_factor,
        ).with_color_configuration(
            bg_hex=bg_hex,
            deselected_font_hex=deselected_font_hex,
            bubble_hex=bubble_hex,
            icon_hex=icon_hex,
        )

        boottext_image = boot_screen.generate_with_text(display_text, icon_path)
        return boottext_image

    def generate_button_glyph(
        self,
        button_text: str,
    ) -> Image.Image:
        glyph_img = self.footer_guides._generate_button_glyph(
            button_text,
            self.manager.physical_controller_layout_var,
        )
        glyph_img = change_logo_color(glyph_img, self.manager.footerBubbleHexVar)

        return glyph_img

    def generate_wall_image(
        self,
        right_buttons: list[tuple[str, str]] = [],
        left_buttons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        *args,
    ) -> Image.Image:
        image = self._generate_background()

        header_bubbles_image = self._generate_header_bubbles(*args)
        image.alpha_composite(header_bubbles_image, (0, 0))

        footer_guides_image = self._generate_footer_guides(right_buttons, left_buttons)
        image.alpha_composite(footer_guides_image, (0, 0))

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def generate_static_image(
        self,
        right_buttons: list[tuple[str, str]] = [],
        left_buttons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        *args,
    ) -> Image.Image:
        image = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))

        header_bubbles_image = self._generate_header_bubbles(*args)
        image.alpha_composite(header_bubbles_image)

        footer_guides_image = self._generate_footer_guides(right_buttons, left_buttons)
        image.alpha_composite(footer_guides_image)

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def generate_launcher_image(
        self,
        right_buttons: list[tuple[str, str]] = [],
        left_buttons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        selected_item: str = "explore",
        variant: str | None = None,
        *args,
    ) -> Image.Image:
        variant = variant or self.manager.main_menu_style_var
        if variant == "Vertical":
            return self.generate_static_image(right_buttons, left_buttons)

        image = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))

        launcher_icons_image = self._generate_launcher_icons(selected_item, variant)
        image.alpha_composite(launcher_icons_image)

        header_bubbles_image = self._generate_header_bubbles(selected_item)
        image.alpha_composite(header_bubbles_image)

        footer_guides_image = self._generate_footer_guides(right_buttons, left_buttons)
        image.alpha_composite(footer_guides_image)

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def generate_boot_logo_image(
        self,
    ) -> Image.Image:
        image = self._generate_background()

        bootlogo_image = self._generate_boot_logo_image()
        image.alpha_composite(bootlogo_image, (0, 0))

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def generate_boot_text_image(
        self, display_text: str, icon_path: Path | None = None
    ) -> Image.Image:
        image = self._generate_background()

        boottext_image = self._generate_boot_text_image(display_text, icon_path)
        image.alpha_composite(boottext_image, (0, 0))

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def generate_background_image(
        self,
    ) -> Image.Image:
        image = self._generate_background()
        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def get_fonts(self) -> list[tuple[str, Path]]:
        fonts = [("panel", self.get_font_binary(self.manager.font_size_var))]

        fonts.append(("header", self.header_bubbles.get_font()))
        fonts.append(("footer", self.footer_guides.get_font()))

        return fonts

    def generate_theme(
        self,
        temp_path: Path,
        progress_callback: Callable | None = None,
    ) -> None:
        if progress_callback:
            progress_callback("Copying theme shell...", 5)

        copy_contents(THEME_SHELL_DIR, temp_path)

        resolution = (
            f"{self.manager.deviceScreenWidthVar}x{self.manager.deviceScreenHeightVar}"
        )
        res_path = temp_path / resolution
        font_path = res_path / "font"
        header_glyph_path = res_path / "glyph" / "header"
        footer_glyph_path = res_path / "glyph" / "footer"
        image_path = res_path / "image"
        wall_path = res_path / "image" / "wall"
        static_path = res_path / "image" / "static"
        scheme_path = res_path / "scheme"
        folders = [
            res_path,
            font_path,
            header_glyph_path,
            footer_glyph_path,
            image_path,
            wall_path,
            static_path,
            scheme_path,
        ]

        for folder in folders:
            ensure_folder_exists(folder)

        if self.manager.include_overlay_var:
            if progress_callback:
                progress_callback("Including overlay with theme...", 5)

            src_overlay = (
                OVERLAY_DIR / resolution / f"{self.manager.selected_overlay_var}.png"
            )
            dest_overlay = image_path / "overlay.png"
            shutil.copy2(src_overlay, dest_overlay)

        if progress_callback:
            progress_callback("Generating button glyphs...", 5)

        buttons_to_generate = ["A", "B", "C", "MENU", "X", "Y", "Z"]
        for button in buttons_to_generate:
            glyph_img = self.generate_button_glyph(button)
            glyph_img = glyph_img.resize(
                (
                    int(glyph_img.size[0] / 5),
                    int(glyph_img.size[1] / 5),
                ),
                Resampling.LANCZOS,
            )
            glyph_img.save(footer_glyph_path / f"{button.lower()}.png")

        if progress_callback:
            progress_callback("Generating battery glyphs...", 5)

        glyph_height = int(self.manager.header_glyph_height_var)
        battery_capacities = range(0, 101, 10)
        for capacity in battery_capacities:
            capacity_image_path = (
                GLYPHS_DIR
                / f"{BatteryStyleOptionsDict[self.manager.battery_style_var]}{capacity}[5x].png"
            )
            charging_image_path = (
                GLYPHS_DIR
                / f"{BatteryChargingStyleOptionsDict[self.manager.battery_charging_style_var]}{capacity}[5x].png"
            )
            for idx, img_path in enumerate([capacity_image_path, charging_image_path]):
                glyph_img = Image.open(img_path)
                glyph_img = glyph_img.resize(
                    (
                        int(glyph_height * glyph_img.size[0] / glyph_img.size[1]),
                        glyph_height,
                    ),
                    Resampling.LANCZOS,
                )
                glyph_img.save(
                    header_glyph_path
                    / f"capacity_{'charging_' if idx == 1 else ''}{capacity}.png"
                )

        if progress_callback:
            progress_callback("Generating network glyphs...", 5)

        network_glyph_names = ["network_active", "network_normal"]
        for glyph_name in network_glyph_names:
            network_image_path = GLYPHS_DIR / f"{glyph_name}[5x].png"
            network_img = Image.open(network_image_path)
            network_img = network_img.resize(
                (
                    int(glyph_height * network_img.size[0] / network_img.size[1]),
                    glyph_height,
                ),
                Resampling.LANCZOS,
            )
            network_img.save(header_glyph_path / f"{glyph_name}.png")

        if progress_callback:
            progress_callback("Copying font binaries...", 5)

        for dest, font in self.get_fonts():
            dest_path = font_path / dest
            ensure_folder_exists(dest_path)

            shutil.copy2(font, dest_path / "default.bin")

        if progress_callback:
            progress_callback("Processing menu definitions...", 0)

        menu_defs = read_json(MENU_DEFINITIONS_PATH)
        defaults = menu_defs.get("default", {})
        for name, menu_def in menu_defs.items():
            if (
                (name[:3] == "mux" or name == "default")
                and self.renderer
                and (rendered_scheme := self.renderer.render(name))
            ):
                if progress_callback:
                    progress_callback("Generating scheme files...", 5)

                with (scheme_path / f"{name}.txt").open("w") as f:
                    f.write(rendered_scheme)

            if progress_callback:
                progress_callback("Generating theme images...", 5)

            if name == "bootlogo":
                boot_image = self.generate_boot_logo_image()
                boot_image.save(image_path / "bootlogo.bmp")
                continue
            elif name == "default":
                background_image = self.generate_background_image()
                background_image.save(wall_path / "default.png")
                continue
            elif name == "muxassign":
                continue

            if not menu_def:
                continue
            elif caption_text := menu_def.get("caption_text"):
                icon_path = menu_def.get("icon_path")
                boot_image = self.generate_boot_text_image(
                    caption_text, Path(icon_path) if icon_path else None
                )
                boot_image.save(
                    (wall_path if name[:3] == "mux" else image_path) / f"{name}.png"
                )
                continue

            def_right_buttons = menu_def.get(
                "right_guides", defaults.get("right_guides", [])
            )
            def_left_buttons = menu_def.get(
                "left_guides", defaults.get("left_guides", [])
            )

            if len(menu_items := menu_def.get("menu_items", [])) > 1:
                menu_path = static_path / name
                ensure_folder_exists(menu_path)

                if name == "muxsearch":
                    wall_img = self.generate_wall_image(
                        def_right_buttons, def_left_buttons
                    )
                    wall_img.save(wall_path / f"{name}.png")
                    continue

                for item, item_def in menu_items.items():
                    right_buttons = item_def.get("right_guides", def_right_buttons)
                    left_buttons = item_def.get("left_guides", def_left_buttons)

                    static_img = (
                        self.generate_launcher_image(right_buttons, left_buttons, item)
                        if name == "muxlaunch"
                        else self.generate_static_image(right_buttons, left_buttons)
                    )
                    static_img.save(menu_path / f"{item}.png")
            else:
                wall_img = self.generate_wall_image(def_right_buttons, def_left_buttons)
                wall_img.save(wall_path / f"{name}.png")

        if self.manager.enable_grid_view_explore_var:
            if progress_callback:
                progress_callback("Generatng system logo icons...", 5)

            system_logos_path = (
                temp_path
                / "system_logos"
                / "run"
                / "muos"
                / "storage"
                / "info"
                / "catalogue"
                / "Folder"
                / "grid"
                / "resolutions"
                / resolution
            )
            ensure_folder_exists(system_logos_path)

            self._resize_system_logos(
                SYSTEM_LOGOS_DIR,
                system_logos_path,
                self.renderer.grid_cell_size if self.renderer else 100,
            )

        if progress_callback:
            progress_callback(f"Theme generation completed for {resolution}!", 10)

    def _resize_system_logos(
        self,
        system_logos_path: Path,
        output_system_logos_path: Path,
        grid_cell_size: int,
    ) -> None:
        effective_grid_size = grid_cell_size - 20

        for system_logo in system_logos_path.iterdir():
            if not system_logo.is_file():
                continue

            system_logo_image = Image.open(system_logo).convert("RGBA")
            width_multiplier = effective_grid_size / system_logo_image.size[0]
            height_multiplier = effective_grid_size / system_logo_image.size[1]
            multiplier = min(width_multiplier, height_multiplier)
            new_size = (
                int(system_logo_image.size[0] * multiplier),
                int(system_logo_image.size[1] * multiplier),
            )
            system_logo_image = system_logo_image.resize(new_size, Resampling.LANCZOS)
            system_logo_image.save(output_system_logos_path / system_logo.name)
