from fabric.api import cd, run, task, prefix

import utils


@task
def install():
    """
    Install mercurial in a python virtual environment.

    :Example:

    fab --config=config.conf mercurial.install
    """
    venvs = utils.home('venvs')

    # Create the virtual environment.
    with cd(venvs):
        run('virtualenv mercurial')

    # Activate the virtual environment.
    with prefix('source {}/mercurial/bin/activate'.format(venvs)):
        run('pip install mercurial')
