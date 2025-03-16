import cmd
import shlex
import webbrowser
import process_engine
import json
import os
import traceback

program_name = 'VersaMesh'
build_file = 'build.json'
website = 'https://github.com/christoferpeterson/versamesh'

# Allows for setting dynamic documentation to python CLI functions
def doc(doc):
    def decorator(func):
        func.__doc__ = doc
        return func
    return decorator

class Program(cmd.Cmd):
    intro = f'Welcome to {program_name}. Type help or ? to list commands.\n'
    prompt = '> '

    def __init__(self, build):
        super().__init__()
        self.engine = process_engine.ProcessEngine()
        self.build = build

    @doc(
        """
Updates one or more settings in the processing engine.

Usage:
    set key1=value1 key2="value with spaces" key3=value3
Example:
    set inputFolder=/myData outputFolder="./my output"

Use the 'settings' command to view current values.
        """
    )
    def do_set(self, line):
        try:
           args = shlex.split(line)
           for arg in args:
            if "=" not in arg:
                print(f"Error: Invalid argument '{arg}'. Expected format key=value.")
                continue
            key, value = arg.split("=", 1)
            key, value = key.strip(), value.strip()
            self.engine.update_setting(key, value)
        except Exception as e:
            print(f"Error processing input: {e}")

    @doc(
        """
Runs the simplify step for all specified algorithms step on all meshes 
found in the provided input folder and saves them into the output folder.

Usage:
    process
        """
    )
    @doc(f"Simplify a set of 3D meshes using a given set of algorithms.")
    def do_process(self, arg):
        try:
            self.engine.process()
        except Exception as e:
            traceback_str = traceback.format_exc()
            print(traceback_str)
            print(f"Error simplying files: {e}")

    @doc("""
Displays the current settings.

Usage:
    settings
        """)
    def do_settings(self, arg):
        for key, value in self.engine.settings.items():
            print(f"{key} = {value}")

    @doc("""
Analyze the simplified and smoothed meshes.
         
Usage:
    analyze
""")
    def do_analyze(self, line):
        try:
            self.engine.analyze()
        except Exception as e:
            print(f"Analysis failed. Details: {e}")

    @doc(f"Opens the {program_name} website in a web browser.")
    def do_website(self, arg):
        try:
            webbrowser.open(website)
        except:
            print(f"Visit {website} for detailed information about {program_name}.")
        
    def do_about(self, arg):
        print(f"Version: {self.build['__version__']}")

    @doc("Exits the program.")
    def do_exit(self, arg):
        print("Exiting...")
        return True

if __name__ == '__main__':
    build = {}
    if(os.path.exists(build_file)):
        with open(build_file) as f:
            build = json.load(f)

    print(""" _____                 _____         _   """)
    print("""|  |  |___ ___ ___ ___|     |___ ___| |_ """)
    print("""|  |  | -_|  _|_ -| .'| | | | -_|_ -|   |""")
    print(f""" \\___/|___|_| |___|__,|_|_|_|___|___|_|_| v{build['__version__']}""")
    Program(build).cmdloop()