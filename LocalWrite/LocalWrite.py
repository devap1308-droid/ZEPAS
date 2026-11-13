import os
import shlex
import shutil as sh
from pathlib import Path

print("CWD  " + os.getcwd())


class Commands:
    _RESERVED_WIN_NAMES = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    @staticmethod
    def _safe_path(target, allow_root=False):
        base_dir = Path.cwd().resolve()
        resolved_target = (base_dir / target).resolve()
        if not resolved_target.is_relative_to(base_dir):
            raise PermissionError(
                f"Access denied: '{target}' escapes the workspace."
            )
        if not allow_root and resolved_target == base_dir:
            raise PermissionError(
                f"Access denied: cannot target workspace root ('{target}')."
            )
        if os.name == "nt":
            for part in resolved_target.relative_to(base_dir).parts:
                if part.split(".")[0].upper() in Commands._RESERVED_WIN_NAMES:
                    raise PermissionError(
                        f"Access denied: '{target}' uses a reserved Windows device name.")

        return resolved_target

    @staticmethod
    def mkdir(folder_name):
        """mkdir[command] -> make a single folder
        Syntax: mkdir <folder_name>"""
        folder_path = Commands._safe_path(folder_name)
        os.mkdir(folder_path)

    @staticmethod
    def mknestdir(folder_path):
        """mknestdir[command] -> make a nested folder
        Syntax: mknestdir <folder_path>"""
        nested_path = Commands._safe_path(folder_path)
        nested_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def touch(file_name):
        """touch[command] -> create an empty file
        Syntax: touch <file_name>"""

        file_name = file_name.rstrip(".")

        if not Path(file_name).suffix:
            file_name = file_name + ".txt"

        file_path = Commands._safe_path(file_name)
        file_path.touch()

    @staticmethod
    def copy(src, dst):
        """copy[command] -> copy source to destination
        Syntax: copy <src> <dst>"""
        source_path = Commands._safe_path(src)
        destination_path = Commands._safe_path(dst)
        sh.copy2(source_path, destination_path)

    @staticmethod
    def rm(file_name):
        """rm[command] -> remove a file
        Syntax: rm <file_name>"""
        file_path = Commands._safe_path(file_name)
        os.remove(file_path)

    @staticmethod
    def write(text, file_name):
        """write[command] -> write a file
        Syntax: write <text> <file_name>"""

        file_name = file_name.rstrip(".")

        if not Path(file_name).suffix:
            file_name = file_name + ".txt"

        file_path = Commands._safe_path(file_name)
        file_path.write_text(text)

    @staticmethod
    def rmdir(folder_name):
        """rmdir[command] -> remove a folder
        Syntax: rmdir <folder_name>"""
        folder_path = Commands._safe_path(folder_name)
        os.rmdir(folder_path)

    @staticmethod
    def rmnestdir(folder_name):
        """rmnestdir[command] -> remove a nested folder
        Syntax: rmnestdir <folder_name>"""
        nested_path = Commands._safe_path(folder_name)
        sh.rmtree(nested_path)

    @staticmethod
    def ls():
        r"""ls[command] -> list all directories and files, directories end with \ or / accordingly
        Syntax: ls """
        print("\n".join(f if "." in f else f"{f}/" for f in sorted(os.listdir())))

    @staticmethod
    def clear():
        """clear [command] -> clears the terminal screen
        Syntax: clear"""

        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    @classmethod
    def help(cls, target=None):
        """help [command] -> Lists all available documentation or a specific command's doc.
        Syntax: help , OR , help <command>"""

        if target is not None:
            target_attr = getattr(cls, target, None)
            if target_attr and callable(target_attr) and not target.startswith("_"):
                print("\n")
                print(f"Documentation for {target}")
                print(target_attr.__doc__)
                print("\n")


        else:
            for name in dir(Commands):
                if name.startswith("_"):
                    continue

                target_attr = getattr(Commands, name)

                if callable(target_attr):
                    print(f"Function: {name}")
                    print(f"Documentation: {target_attr.__doc__} \n")


while True:
    try:
        UserInput = input(f"{Path.cwd()}$> ").strip()
        if not UserInput:
            continue

        parts = [p[1:-1] if len(p) >= 2 and p[0] == p[-1] and p[0] in ('"', "'") else p
                 for p in shlex.split(UserInput, posix=(os.name != "nt"))]
        user_command = parts[0].lower()
        args = parts[1:]

        if user_command in ("exit", "quit"):
            break

        attr = getattr(Commands, user_command, None)
        if attr is not None:
            if callable(attr) and not user_command.startswith("_"):
                attr(*args)

        if attr is None:
            print(f"Command '{user_command}' not found")
            continue

    except Exception as e:
        print(e)
        continue
