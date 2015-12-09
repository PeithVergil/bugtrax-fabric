from fabric.api import sudo, task


@task
def install():
    """
    Install ufw.

    :Example:

    fab --config=config.conf ufw.install
    """
    sudo('apt-get -y install ufw')


@task
def default(action='deny'):
    """
    Set the default action when ufw is enabled. Default to "deny".

    :Example:

    fab --config=config.conf ufw.default
    """
    sudo('ufw default {}'.format(action))


@task
def allow(service):
    """
    Allow a service access through the firewall.

    :Example:

    fab --config=config.conf ufw.allow
    """
    sudo('ufw allow {}'.format(service))


@task
def enable():
    """
    Enable the firewall.

    :Example:

    fab --config=config.conf ufw.enable
    """
    sudo('ufw --force enable')
