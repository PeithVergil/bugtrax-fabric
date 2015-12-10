from fabric.api import sudo, task


@task
def install():
    """
    Install supervisor.
    """
    sudo('apt-get -y install supervisor')


@task
def restart():
    """
    Restart the supervisor service.

    :Example:

    fab --config=config.conf supervisor.restart
    """
    sudo('service supervisor restart')


@task
def start():
    """
    Start the supervisor service.
    """
    sudo('service supervisor start')


@task
def stop():
    """
    Stop the supervisor service.
    """
    sudo('service supervisor stop')


@task
def ctl_reread():
    """
    Read the changes from the configuration files.

    :Example:

    fab --config=config.conf supervisor.ctl_reread
    """
    sudo('supervisorctl reread')


@task
def ctl_update():
    """
    Update supervisor to enable the changes.

    :Example:

    fab --config=config.conf supervisor.ctl_reread
    """
    sudo('supervisorctl update')
