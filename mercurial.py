from fabric.api import cd, run, sudo, task, prefix

import utils


@task
def install():
    """
    Install mercurial in a python virtual environment.

    :Example:

    fab --config=config.conf mercurial.install
    """
    # Python build headers.
    packages = [
        'python-setuptools',
        'python-virtualenv',
        'python-dev',
        'python-tk',
    ]

    # Install python build headers.
    sudo('apt-get -y install {}'.format(' '.join(packages)))

    # Put all virtual environments in one directory.
    run('mkdir -p {}'.format(utils.home('venvs')))

    # Create the virtual environment.
    venvs = utils.home('venvs')

    with cd(venvs):
        run('virtualenv mercurial')

    # Activate the virtual environment.
    with prefix('source {}/mercurial/bin/activate'.format(venvs)):
        run('pip install mercurial')
