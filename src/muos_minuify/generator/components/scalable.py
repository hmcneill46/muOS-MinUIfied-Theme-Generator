class Scalable:
    def __init__(
        self,
        screen_dimensions: tuple[int, int] = (640, 480),
        render_factor: int = 1,
    ):
        self.screen_dimensions = screen_dimensions
        self.render_factor = render_factor

    @property
    def scaled_screen_dimensions(self) -> tuple[int, int]:
        return (
            int(self.screen_dimensions[0] * self.render_factor),
            int(self.screen_dimensions[1] * self.render_factor),
        )
