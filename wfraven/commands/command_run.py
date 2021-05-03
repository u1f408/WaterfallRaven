import uuid
import toml
import waitress
import psycopg2

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.flask import FlaskIntegration

from wfraven.cli import subcommand
from wfraven.utils import update_database_pointer
from wfraven.app import app


@subcommand()
def run(*args):
    """Run Raven.
    """
    
    # Load the configuration
    with open('raven.toml', 'r') as fh:
        config = toml.loads(fh.read())
        if config is None:
            print("Failed to load config")
            return 1
    
    # Update the database pointer
    if not update_database_pointer(config):
        print("Failed to update database pointer")
        return 1

    # Configure Sentry
    if config['server']['sentry_dsn'] is not False:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.WARNING,
        )

        sentry_sdk.init(
            dsn=config['server']['sentry_dsn'],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
        )

    # Configure application
    app.config['RAVEN_SERVER_ID'] = config['server']['id']
    app.config['RAVEN_CONFIG'] = config

    # Serve the application
    waitress.serve(app, host='0.0.0.0', port=6968, threads=250, connection_limit=250)
    return 0
