import uuid
import toml
import psycopg2

from wfraven.cli import subcommand
from wfraven.utils import update_database_pointer


@subcommand()
def pointer(*args):
    """Attempt to add or update the database pointer to this instance
    """
    
    with open('raven.toml', 'r') as fh:
        config = toml.loads(fh.read())
        if config is None:
            print("Failed to load config")
            return 1

    # Explain and ask for base_host
    print("")
    print(
        "Now we need to know the IP address (or hostname) of the server that this" +
        " Raven instance is running on. This will be inserted into the database," +
        " and is what Waterfall uses to communicate with this Raven instance." +
        " You can just press Enter here if this Raven instance is running on the" +
        " same machine as the Waterfall web server (which will generally be the" +
        " case in development)."
    )

    base_host = input("Server IP or hostname [127.0.0.1]: ")
    if base_host is None or base_host.strip() == "":
        base_host = "127.0.0.1"

    # Add pointer to this Raven instance to the database
    print("Attempting database entry... ", end="")
    if update_database_pointer(config, base_host=base_host):
        print("done!")
    else:
        print("failed!")
        return 101

    print("Database pointer added/updated. You can start Raven with `wfraven start`.")
    return 0
