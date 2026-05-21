import os
import subprocess
import sys
from collections.abc import Callable

CommandFunc = Callable[[list[str]], str]
COMMANDS: dict[str, CommandFunc] = {}


def register_command(name: str) -> Callable[[CommandFunc], CommandFunc]:
    def wrapper(func: CommandFunc) -> CommandFunc:
        COMMANDS[name] = func
        return func

    return wrapper


@register_command("echo")
def echo(args: list[str]) -> str:
    return " ".join(args) + "\n"


def test():
    # os.access(path, os.X_OK)

    path_env = os.environ.get("PATH", "")

    # Split it into a list of directories
    directories = path_env.split(":")
    for dir in directories:
        print(dir)


@register_command("type")
def type_cmd(args: list[str]) -> str:
    if not args:
        return ""
    lines = []

    for arg in args:
        if arg in COMMANDS:
            lines.append(f"{arg} is a shell builtin")
            continue
        if cmd_path := find_executable(arg):
            lines.append(f"{arg} is {cmd_path}")
        else:
            lines.append(f"{arg}: not found")

    return "\n".join(lines) + "\n"


class ExitShell(Exception):
    """Exception to signal the shell should close."""

    pass


# --- Helper functions --------------------------------------------------------
def find_executable(command: str) -> str:
    paths_env = os.getenv("PATH", "")
    if not paths_env:
        return ""
    paths = paths_env.split(os.pathsep)
    for path in paths:
        full_path = os.path.join(path, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return ""


@register_command("exit")
def exit_cmd(args: list[str]) -> str:
    raise ExitShell()


def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        line = sys.stdin.readline()

        user_input = line.strip()
        if not user_input:
            continue

        command, args = parse_command(user_input)

        try:
            if handler := COMMANDS.get(command):
                sys.stdout.write(handler(args))
            elif find_executable(command):
                subprocess.run([command] + args)
            else:
                sys.stdout.write(f"{command}: command not found\n")
        except ExitShell:
            break


# Get the PATH string from the environment
def parse_command(arg: str) -> tuple[str, list[str]]:
    args = arg.split()
    command = args.pop(0)
    return (command, args)


if __name__ == "__main__":
    main()
