import psutil
import random
import hashlib
import platform
import psycopg2

from datetime import datetime


FILENAME_CHARS = [chr(x) for x in range(65, 91)] + [chr(x) for x in range(97, 123)]


def generate_filename():
    return ''.join(random.sample(FILENAME_CHARS, 25))


def generate_datehash_and_directory():
    random_int = random.randrange(1, 999999)
    date_hash = hashlib.md5(datetime.now().isoformat().encode("utf-8")).hexdigest()
    directory = hashlib.md5(f"{date_hash}{random_int}".encode("utf-8")).hexdigest()
    return (date_hash, directory)


def get_storage_size(base_dir):
    """Get available and total storage size of the `base_dir`
    
    On Windows, this just checks the disk usage of `C:`
    """

    if any(platform.win32_ver()):
        disk = psutil.disk_usage('C:')
    else:
        disk = psutil.disk_usage(base_dir)

    # Theoretically, kilobytes
    storage_available = disk.free / 1024
    storage_total = disk.total / 1024
    
    return (storage_available, storage_total)


def get_hardware_score():
    """Generate an arbitrary score for hardware.
    """

    # RAM, in megabytes
    memory_mb = psutil.virtual_memory()[0] / (1024 * 1024)

    # CPU scoring
    cpu_freq = psutil.cpu_freq()
    cpu_score = psutil.cpu_count() * cpu_freq.max
    
    # Load average over 15 minutes
    load_value = psutil.getloadavg()[2]
    if load_value == 0.0:
        load_value = 10
        
    final_score = (memory_mb + cpu_score) / load_value
    return final_score


def update_database_pointer(config, base_host=None, base_port='6968'):
    """Create or update the pointer in the Waterfall database to this
    Raven instance.
    
    If a pointer does not exist for the server ID given in the `config`,
    this will create a new one using the `base_host` keyword parameter as
    the IP/hostname for the pointer.
    
    If a pointer does exist for the server ID given in the `config`, this
    will update that pointer with the current Raven server information.
    Optionally, if the `base_host` keyword parameter is not `None`, this
    will update the IP/hostname of the pointer to the given `base_host`.
    
    Returns a boolean indicating success.
    """
    
    connection = psycopg2.connect(**config['database'])
    cursor = connection.cursor()
    if not cursor.connection:
        return False
        
    (storage_available, storage_total) = get_storage_size(config['server']['base_dir'])
    hardware_score = get_hardware_score()
    
    # Check if a pointer exists with the given server ID
    cursor.execute("SELECT * FROM raven_servers WHERE id = %s", [config['server']['id']])
    current_pointer = cursor.fetchall()
    if current_pointer == []:
        # We need to create a new pointer
        if base_host is None or base_host.strip() == '':
            return False

        values = [
            config['server']['id'],
            config['server']['name'],
            base_host,
            base_port,
            'content', # other types are deprecated
            storage_available,
            storage_total,
            hardware_score, 
            config['server']['verify_key'],
        ]

        cursor.execute("""INSERT INTO raven_servers (
            id,
            server_name,
            server_ip,
            server_port,
            server_role,
            storage_available,
            storage_total,
            hardware_score,
            verify_key
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)
        connection.commit()
        return True

    if base_host is None:
        base_host = current_pointer[0][2]
        base_port = current_pointer[0][3]

    values = [
        base_host,
        base_port,
        storage_available,
        storage_total,
        hardware_score, 
        config['server']['id'],
    ]
    
    cursor.execute("""UPDATE raven_servers SET
        server_ip = %s,
        server_port = %s,
        storage_available = %s,
        storage_total = %s, 
        hardware_score = %s
    WHERE id = %s""", values)
    connection.commit()
    return True
