from fabric.api import require, prefix, sudo, task, env, put, run, cd
from fabric.contrib import files

import utils


@task
def clone():
    """
    Clone the project repository.

    :Example:

    fab --config=config.conf project.clone
    """
    require('PROJECT_NAME')
    require('PROJECT_REPO')
    require('MERCURIAL_BIN')

    # Create the "apps" directory if it does not exist.
    run('mkdir -p {}'.format(utils.home('apps')))

    if files.exists(utils.home('apps', env.PROJECT_NAME)):
        delete()

    with cd(utils.home('apps')):
        run('{0} clone {1} {2}'.format(env.MERCURIAL_BIN,
                                       env.PROJECT_REPO,
                                       env.PROJECT_NAME))


@task
def config():
    """
    Upload production settings file.

    :Example:

    fab --config=config.conf project.config
    """
    project = env.PROJECT_NAME

    filename = 'prod.py'

    local_file = utils.file_path('project', filename)

    remote_file = utils.home('apps', project, 'config', 'settings', filename)

    put(local_file, remote_file)


@task
def migrate():
    """
    Run database migrations.

    :Example:

    fab --config=config.conf project.migrate
    """
    require('PROJECT_VENV')
    require('PROJECT_NAME')

    venv = utils.home('venvs', env.PROJECT_VENV)

    with prefix('source {0}/bin/activate'.format(venv)):
        with cd(utils.home('apps', env.PROJECT_NAME)):
            run('python manage.py migrate --settings=config.settings.prod')


@task
def collectstatic():
    """
    Deploy static files.

    :Example:

    fab --config=config.conf project.collectstatic
    """
    require('PROJECT_VENV')
    require('PROJECT_NAME')

    venv = utils.home('venvs', env.PROJECT_VENV)

    with prefix('source {0}/bin/activate'.format(venv)):
        with cd(utils.home('apps', env.PROJECT_NAME)):
            run('python manage.py collectstatic --noinput --settings=config.settings.prod')


@task
def restart():
    """
    Restart the project process.

    :Example:

    fab --config=config.conf project.restart
    """
    require('PROJECT_NAME')

    sudo('supervisorctl restart {0}'.format(env.PROJECT_NAME))


def update():
    """
    Pull the latest changes from the remote repo.
    """
    require('PROJECT_NAME')

    with cd(utils.home('apps', env.PROJECT_NAME)):
        run('hg pull')
        run('hg up')


def delete():
    """
    Delete the cloned repo from the server.
    """
    run('rm -r {}'.format(utils.home('apps', env.PROJECT_NAME)))
