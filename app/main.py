import sys


def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input().lower()
        command, args = parse_command(user_input)
        if command == "exit":
            break
        elif command == "echo":
            sys.stdout.write(" ".join(args) + "\n")
        else:
            sys.stdout.write(f"{command}: command not found\n")


def parse_command(arg: str) -> tuple[str, list[str]]:
    args = arg.split()
    command = args.pop(0)
    return (command, args)


if __name__ == "__main__":
    main()
