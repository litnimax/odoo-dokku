import logging
import re
import os
import subprocess
import sys

"""
This Odoo launcher script starts Odoo with arguments taken from:
- Dsn set by dokku when linking with postgres instance (DATABASE_URL);
- ODOO_ARG_... environent variables;
- arguments passed to docker run CMD.
"""

# Set default logging
logging.basicConfig(level=logging.INFO)

# Adjust volume permissions
data_dir = os.environ.get('DATA_DIR') or '/var/lib/odoo'
subprocess.check_call(['chown', '-R', 'odoo:odoo', data_dir])

# Dictionaly of odoo arguments
odoo_args_dict = {}

# Populate odoo args with values from Dsn
found = re.search('^postgres://postgres:(.+)@(.+):(.+)/(.+)$', os.environ.get('DATABASE_URL', ''))
if found:
    logging.info('Getting connection from Dsn.')
    odoo_args_dict['db_password'] = found.group(1)
    odoo_args_dict['db_host'] = found.group(2)
    odoo_args_dict['db_port'] = found.group(3)
    odoo_args_dict['database'] = found.group(4)
else:
    logging.info('Dsn not found. Looking for ODOO_ARG_ variables.')

# Some odoo args are used with _, some with -, like --db-filter and db_name.
keep_args = ['db_user', 'db_host', 'db_port',  'db_password',
             'db_sslmode', 'db_maxconn', 'pg_path']

# Check env vars
odoo_env = filter(lambda a: a.startswith('ODOO_ARG'), os.environ.keys())
for arg in odoo_env:
    # Get value
    val =os.environ.get(arg)
    # Convert argument to odoo format
    cast_arg = arg.replace('ODOO_ARG_', '').lower()
    if cast_arg not in keep_args:
        # Replace _ with -
        cast_arg = cast_arg.replace('_', '-')
    #
    logging.info('Setting {} to {}.'.format(cast_arg, val))
    if odoo_args_dict.get(cast_arg):
        logging.info('Overriding {} with {}.'.format(cast_arg, val))
    odoo_args_dict[cast_arg] = val

"""
# Now let see if docker run CMD arguments where given to override
if sys.argv[1] in ['odoo', 'odoo.py']:
    # Check if odoo arguments where given in dsn / vars
    if len(sys.argv) > 1:
        for arg in sys.argv[2:]:
            arg, val = arg.split('=') if arg.find('=') != -1 else (arg, '')
            arg = arg.replace('-','')
            if odoo_args_dict.get(arg):
                logging.info('Overriding {} with {}.'.format(arg, val))
            else:
                logging.info('Setting {} to {}.'.format(arg, val))
            odoo_args_dict[arg] = val
"""

# Transform args to command line args
odoo_args = []
for arg, val in odoo_args_dict.items():
    if val:
        odoo_args.append('--{}={}'.format(arg, val))
    else:
         odoo_args.append('--{}'.format(arg))
# Add command line args
if len(sys.argv) > 1:
    odoo_args.extend(sys.argv[2:])


# Start default odoo entrypoint
if len(sys.argv) == 1:
    logging.error('You must call entrypoint.py with some args.')
    sys.exit(1)

print (odoo_args)
# Default cmd
if sys.argv[1] in ['odoo', 'odoo.py']:
    logging.info('Starting: {} {}'.format(sys.argv[1], ' '.join(odoo_args)))
    os.execvp('gosu', ['gosu', 'odoo', sys.argv[1]] + odoo_args)

else:
    logging.info('Starting {}.'.format(sys.argv))
    os.execvp(sys.argv[1], sys.argv[1:])
