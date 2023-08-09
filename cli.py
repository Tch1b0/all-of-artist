class CLI:
    args: list[str]
    interactive: bool

    def __init__(self, args: list[str]) -> None:
        self.args = args

        self.interactive = "--not-interactive" not in self.args
