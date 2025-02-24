class Scalable:
    def __init__(
        self,
        screen_dimensions: tuple[int, int] = (640, 480),
        render_factor: int = 1,
        **kwargs,
    ):
        self.screen_dimensions = screen_dimensions
        self.render_factor = render_factor

        super().__init__(**kwargs)

    @property
    def scaled_screen_dimensions(self) -> tuple[int, int]:
        return (
            int(self.screen_dimensions[0] * self.render_factor),
            int(self.screen_dimensions[1] * self.render_factor),
        )
