import getpass
import os

def _set_env(var: str):
    """
    if environment variable not set, safely prompts user for value
    returns the newly resolved variable
    """
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")
    return os.environ[var]
