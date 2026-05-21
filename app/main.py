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


@register_command("pwd")
def pwd(args: list[str]) -> str:
    return os.getcwd() + "\n"


@register_command("cd")
def cd(args: list[str]) -> str:
    if len(args) > 1:
        return f"cd: string not in pwd: {args[0]}\n"
    target_dir = args[0] if args else os.path.expanduser("~")
    if target_dir.startswith("~"): 
        target_dir = os.path.expanduser(target_dir)
        
    try:
        os.chdir(target_dir)
        return ""
    except FileNotFoundError:
        return f"cd: {target_dir}: No such file or directory\n"
    except PermissionError:
        return f"cd: {target_dir}: Permission denied\n"


class ExitShell(Exception):
    """Exception to signal the shell should close."""

    pass


@register_command("exit")
def exit_cmd(args: list[str]) -> str:
    raise ExitShell()


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
