from fabric.api import env, run, task, sudo, require
from fabric.contrib import files

import utils


@task
def info():
    """
    Get some details about the remote system.

    :Example:

    fab --config=config.conf system.info
    """

    run('uname -a')


@task
def update():
    """
    Update the system packages.

    :Example:

    fab --config=config.conf system.update
    """

    sudo('apt-get -y update')
    sudo('apt-get -y upgrade')


@task
def shutdown():
    """
    Shutdown the server.

    :Example:

    fab --config=config.conf system.shutdown
    """

    sudo('shutdown -h now')


@task
def autoremove():
    """
    Remove unused system packages.

    :Example:

    fab --config=config.conf system.autoremove
    """

    sudo('apt-get -y autoremove')


@task
def user_create(username, password):
    """
    Create a new system user with sudo privileges.

    :param username: The new username.
    :param password: The raw password.

    :Example:

    fab --config=config.conf system.user_create:username=hello,password=world
    """

    result = add_usr(username)

    if result.succeeded:
        add_grp(username, 'sudo')

    if result.succeeded:
        set_pwd(username, password)

    return result.succeeded


@task
def user_delete(username):
    """
    Delete an existing system user.

    :param username: The user to delete.

    :Example:

    fab --config=config.conf system.user_delete:username=hello
    """

    sudo('deluser {}'.format(username))


@task
def user_sshkey(username):
    """
    Upload an SSH key to the remote system for the current user.

    :Example:

    fab --config=config.conf system.user_sshkey:username=hello
    """

    require('PUBLIC_SSH_KEY')

    with open(env.PUBLIC_SSH_KEY) as reader:
        key = reader.read()

    remote_directory = '/home/{}/.ssh'.format(username)
    remote_authkeys = '/home/{}/.ssh/authorized_keys'.format(username)

    new_directory = False

    if not files.exists(remote_directory):
        new_directory = True

        # Create the ".ssh" directory.
        sudo('mkdir -p {}'.format(remote_directory))

    # Add the key to "authorized keys".
    files.append(remote_authkeys, key, use_sudo=True)

    if new_directory:
        # Set permissions.
        sudo('chmod 700 {}'.format(remote_directory))
        sudo('chmod 600 {}'.format(remote_authkeys))

        # Set owners.
        sudo('chown {}:{} {}'.format(username, username, remote_directory))
        sudo('chown {}:{} {}'.format(username, username, remote_authkeys))


def add_usr(username):
    """
    Create a new system user with no password.
    """
    return sudo('adduser --disabled-password --gecos "" {}'.format(username))


def add_grp(username, group):
    """
    Add an existing user to a group.
    """
    return sudo('adduser {} {}'.format(username, group))


def set_pwd(username, password):
    """
    Set a password to an existing user.
    """

    # Hash the raw password.
    password = utils.hash(password)

    return sudo("echo '{}:{}' | chpasswd -e".format(username, password))


@task
def ssh_disable_password_authentication():
    """
    Disable password authentication.

    :Example:

    fab --config=config.conf system.ssh_disable_password_authentication
    """
    filename = '/etc/ssh/sshd_config'

    # Uncomment the setting if necessary.
    if files.contains(filename, '#PasswordAuthentication', use_sudo=True):
        files.uncomment(filename, '#PasswordAuthentication', use_sudo=True)

    # Disable password authentication.
    files.sed(filename,
              'PasswordAuthentication yes',
              'PasswordAuthentication no',
              use_sudo=True)


@task
def ssh_disable_root_login():
    """
    Disable root login.

    :Example:

    fab --config=config.conf system.ssh_disable_root_login
    """
    filename = '/etc/ssh/sshd_config'

    # Disable root login by public keys.
    files.sed(filename,
              'PermitRootLogin without-password',
              'PermitRootLogin no',
              use_sudo=True)

    # Disable root login by username and password.
    files.sed(filename,
              'PermitRootLogin yes',
              'PermitRootLogin no',
              use_sudo=True)


@task
def ssh_restart():
    """
    Restart the SSH server.

    :Example:

    fab --config=config.conf system.ssh_restart
    """
    sudo('service ssh restart')
