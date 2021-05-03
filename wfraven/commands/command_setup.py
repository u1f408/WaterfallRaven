import uuid
import toml
import psycopg2

from wfraven.cli import subcommand
from wfraven.utils import update_database_pointer


CONFIG_PROMPTS = [
    ("Database host", (lambda c, x: c['database'].__setitem__('host', x)),),
    ("Database user", (lambda c, x: c['database'].__setitem__('user', x)),),
    ("Database password", (lambda c, x: c['database'].__setitem__('password', x)),),
    ("Database name", (lambda c, x: c['database'].__setitem__('database', x)),),
    ("Server ID", (lambda c, x: c['server'].__setitem__('id', int(x))),),
    ("Server name", (lambda c, x: c['server'].__setitem__('name', x)),),
    ("Content base directory", (lambda c, x: c['server'].__setitem__('base_dir', x)),),
    ("Sentry DSN", (lambda c, x: c['server'].__setitem__('sentry_dsn', x if x.strip() != '' else False)),),
]


@subcommand()
def setup(*args):
    """Interactively set up Raven
    
    This will prompt for configuration variables for Raven, and create the
    entry in the Waterfall database for the configured Raven instance.
    """
    
    config = {'database': {}, 'server': {}}
    
    # Get our config values
    print("We're going to ask you some questions in order to set up this Raven instance.")
    for (prompt, fn) in CONFIG_PROMPTS:
        value = input(f"{prompt}: ")
        fn(config, value)

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

    # Print the configuration and ask for confirmation
    print("")
    print("Here's the base configuration you've provided: ", end="\n\n")
    print(toml.dumps(config))
    if config['server']['sentry_dsn'] is False:
        print(
            "NOTE: Make sure you edit this configuration and add a Sentry DSN" +
            " before using this Raven instance in production!"
        )

    if input("Is this okay? (Y or N): ").strip().lower() != 'y':
        print("Cancelled. Run `wfraven setup` again to restart Raven setup.")
        return 1

    print("")

    # Test database connection
    print("Testing database connection... ", end="")
    connection = psycopg2.connect(**config['database'])
    cursor = connection.cursor()
    if cursor.connection:
        print("okay!")
    else:
        print("failed!")
        print("Please check your database configuration settings and try again.")
        return 101

    # Populate generated configuration values and write the config
    config['server']['verify_key'] = str(uuid.uuid4())
    print("Writing configuration to `raven.toml`... ", end="")
    with open('raven.toml', 'w') as fh:
        fh.write(toml.dumps(config))
        print("done!")

    # Add pointer to this Raven instance to the database
    print("Attempting database entry... ", end="")
    if update_database_pointer(config, base_host=base_host):
        print("done!")
    else:
        print("failed!")
        print("Adding the pointer to this Raven instance to the database failed.")
        print(
            "Your configuration has been written, and at this point you can run" +
            " `wfraven pointer` to attempt adding the pointer again. Once that" +
            " command is successful, you can start Raven with `wfraven start`."
        )
        return 102
        
    print("This Raven instance has been successfully set up.")
    print("You can start Raven with `wfraven start`.")
    return 0
