from fabric.api import require, sudo, task, env, put, run
from fabric.contrib import files

import utils


@task
def install():
    """
    Install Nginx.

    :Example:

    fab --config=config.conf nginx.install
    """
    sudo('apt-get -y install nginx')


@task
def restart():
    """
    Restart the nginx service.

    :Example:

    fab --config=config.conf nginx.restart
    """
    sudo('service nginx restart')


@task
def start():
    """
    Start the nginx service.

    :Example:

    fab --config=config.conf nginx.start
    """
    sudo('service nginx start')


@task
def stop():
    """
    Stop the nginx service.

    :Example:

    fab --config=config.conf nginx.stop
    """
    sudo('service nginx stop')


@task
def config():
    """
    Upload a custom configuration file.

    :Example:

    fab --config=config.conf nginx.config
    """
    local = utils.file_path('nginx', 'default')

    remote = '/etc/nginx/sites-available/default'
    target = '/etc/nginx/sites-enabled/default'

    put(local, remote, mode='0644', use_sudo=True)

    # Change owner to "root".
    sudo('chown root:root {}'.format(remote))

    # Remove old symlink.
    sudo('rm {}'.format(target))

    # Create new symlink.
    sudo('ln -s {} {}'.format(remote, target))

    # Create the nginx log directory.
    run('mkdir -p {}'.format(utils.home('logs', 'nginx')))


@task
def public():
    """
    Create the public directories.

    :Example:

    fab --config=config.conf nginx.public
    """
    require('PROJECT_NAME')

    media_dir = utils.home('public', env.PROJECT_NAME, 'media')
    static_dir = utils.home('public', env.PROJECT_NAME, 'static')

    run('mkdir -p {}'.format(media_dir))
    run('mkdir -p {}'.format(static_dir))
