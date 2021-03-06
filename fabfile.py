"""
Tasks for automating the setup and deployment of a Django project.

:Example:

fab --config=config.conf system.info
"""

from fabric.api import env, task, execute, require, settings

import supervisor
import mercurial
import project
import python
import system
import nginx
import ufw


require('SYSTEM_USER')
require('SYSTEM_PASS')

env.user, env.password = env.SYSTEM_USER, env.SYSTEM_PASS

env.hosts = [
    env.HOST
]


@task
def setup():
    """
    Provision the remote server.

    :Example:

    fab --config=config.conf setup
    """
    # Ignore errors if the user already exists.
    with settings(user=env.ROOT_USER, password=env.ROOT_PASS, warn_only=True):
        # Create a new system user.
        result = execute('system.user_create',
                         env.SYSTEM_USER,
                         env.SYSTEM_PASS)

        # Upload SSH key for the new system.
        if result.get(env.host):
            execute('system.user_sshkey', env.SYSTEM_USER)

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

    # Install supervisor
    execute('supervisor.install')

    # Install mercurial
    execute('mercurial.install')

    # Install nginx
    execute('nginx.install')
    execute('nginx.config')
    execute('nginx.restart')

    # Setup Python Environment.
    require('PYTHON_VENV')

    execute('python.dev')
    execute('python.venv', env.PYTHON_VENV)
    execute('python.install', env.PYTHON_VENV)

    # Deploy the project.
    #
    # fab --config=config.conf project.clone \
    #                          project.config \
    #                          project.migrate \
    #                          project.collectstatic \
    #                          project.restart
    execute('project.clone')
    execute('project.config')
    execute('project.migrate')
    execute('project.collectstatic')
    execute('project.restart')

    execute('supervisor.restart')
    execute('supervisor.reread')
    execute('supervisor.update')
