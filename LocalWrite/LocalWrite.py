import os
from pathlib import Path
import shutil as sh
import shlex

print("CWD  " + os.getcwd())

class Commands:
    @staticmethod
    def mkdir(folder_name):
        """mkdir[command] -> make a single folder"""
        folder_path = Path(os.getcwd()).joinpath(folder_name)
        os.mkdir(folder_path)

    @staticmethod
    def mknestdir(folder_path):
        """mknestdir[command] -> make a nested folder"""
        nested_path = Path(os.getcwd()).joinpath(folder_path)
        nested_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def touch(file_name):
        """touch[command] -> create an empty file"""
        file_path = Path(os.getcwd()).joinpath(file_name)
        file_path.touch()

    @staticmethod
    def copy(src, dst):
        """copy[command] -> copy source to destination"""
        source_path = Path(os.getcwd()).joinpath(src)
        destination_path = Path(os.getcwd()).joinpath(dst)
        sh.copy2(source_path, destination_path)

    @staticmethod
    def rm (file_name):
        """rm[command] -> remove a file"""
        file_path = Path(os.getcwd()).joinpath(file_name)
        os.remove(file_path)

    @staticmethod
    def write(text, file_name):
        """write[command] -> write a file"""
        file_path = Path(os.getcwd()).joinpath(file_name)
        file_path.write_text(text)

    @staticmethod
    def rmdir(folder_name):
        """rmdir[command] -> remove a folder"""
        folder_path = Path(os.getcwd()).joinpath(folder_name)
        os.rmdir(folder_path)

    @staticmethod
    def rmnestdir(folder_name):
        """rmnestdir[command] -> remove a nested folder"""
        nested_path = Path(os.getcwd()).joinpath(folder_name)
        sh.rmtree(nested_path)

    @staticmethod
    def clear():
        """clear [command] -> clears the terminal screen"""

        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")


    @classmethod
    def help(cls, target=None):
        """help [command] -> Lists all available documentation or a specific command's doc."""

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
        UserInput = input(f"{Path.cwd()}$> ").lower().strip()
        if not UserInput:
            continue

        parts = shlex.split(UserInput)
        user_command = parts[0]
        args = parts[1:]

        if user_command in ("exit",  "quit"):
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