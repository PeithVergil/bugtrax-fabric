"""
Tasks for automating the setup and deployment of a Django project.

:Example:

fab --config=config.conf system.info
"""

from fabric.api import env, task, execute, require, settings

import project
import python
import system
import ufw


require('SYSTEM_USER')
require('SYSTEM_PASS')

env.user, env.password = env.SYSTEM_USER, env.SYSTEM_PASS

env.hosts = [
    '45.55.143.189',
]


@task
def setup():
    """
    Provision the remote server.

    :Example:

    fab --config=config.conf setup
    """
    new_user = False

    # Ignore errors if the user already exists.
    with settings(user=env.ROOT_USER, password=env.ROOT_PASS, warn_only=True):
        # Create a new system user.
        result = execute('system.user_create',
                         env.SYSTEM_USER,
                         env.SYSTEM_PASS)

        if result.get(env.host):
            new_user = True

    # Upload SSH key for the new system.
    if new_user:
        execute('system.user_sshkey')

    ##############################
    # RUN SERVER UPDATES
    ##############################

    execute('system.update')

    ##############################
    # BASIC SERVER SECURITY
    ##############################

    # Disable password authentication.
    execute('system.ssh_disable_password_authentication')
    # Disable root login.
    execute('system.ssh_disable_root_login')
    # Restart SSH.
    execute('system.ssh_restart')

    # Install ufw
    execute('ufw.install')
    # Deny incoming connections.
    execute('ufw.default')
    # Allow SSH (22/tcp) access.
    execute('ufw.allow', 'ssh')
    # Allow HTTP (80/tcp) access.
    execute('ufw.allow', 'http')
    # Allow HTTPS (443/tcp) access.
    execute('ufw.allow', 'https')
    # Enable the firewall.
    execute('ufw.enable')

    # Setup Python Environment.
    require('PYTHON_VENV')

    execute('python.dev')
    execute('python.venv', env.PYTHON_VENV)
    execute('python.install', env.PYTHON_VENV)

    # Deploy the project.
    execute('project.clone')
    execute('project.config')
    execute('project.migrate')
    execute('project.collectstatic')
    execute('project.restart')
