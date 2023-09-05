from typing import Optional


class CLI:
    args: list[str]
    interactive: bool
    env_path: Optional[str] = None

    def __init__(self, args: list[str]) -> None:
        self.args = args

        self.interactive = "--not-interactive" not in self.args

        ENV_PATH_FLAG = "--env-path"
        if ENV_PATH_FLAG in self.args:
            self.env_path = self.args[self.args.index(ENV_PATH_FLAG) + 1]
