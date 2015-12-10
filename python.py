from fabric.api import cd, env, put, run, task, sudo, prefix, require

import utils


@task
def dev():
    """
    Install dependencies for building Python C extensions.

    :Example:

    fab --config=config.conf python.dev
    """

    # Python build headers.
    packages = [
        'python3-setuptools',
        'python3-dev',
        'python3-tk',
        'python-setuptools',
        'python-dev',
        'python-tk',
    ]

    sudo('apt-get -y install {}'.format(' '.join(packages)))


@task
def venv(name):
    """
    Create a new Python virtual environment.

    :param name: The name of the new virtual environment.

    :Example:

    fab --config=config.conf python.venv:name=myvenv
    """
    venvs_directory = '/home/{}/venvs'.format(env.user)

    # Put all virtual environments in one directory.
    run('mkdir -p {}'.format(venvs_directory))

    # In Ubuntu 14.04, there's an issue with Python 3's built-in pip.
    # So, virtual environments are created without pip.
    with cd(venvs_directory):
        run('python3 -m venv --without-pip {}'.format(name))

    # Activate the virtual environment then manually download and install pip.
    with prefix('source {}/{}/bin/activate'.format(venvs_directory, name)):
        run('curl https://bootstrap.pypa.io/get-pip.py | python')


@task
def install(name):
    """
    Upload and install the dependencies in the requirements file.

    :param name: The name of the virtual environment to use.

    :Example:

    fab --config=config.conf python.install:name=myvenv
    """
    base = '/home/{}/venvs/{}/base.txt'.format(env.user, name)
    prod = '/home/{}/venvs/{}/prod.txt'.format(env.user, name)

    # Upload requirements file.
    put(utils.file_path('requirements', 'base.txt'), base)
    put(utils.file_path('requirements', 'prod.txt'), prod)

    # Activate the virtual environment.
    with prefix('source /home/{}/venvs/{}/bin/activate'.format(env.user, name)):
        run('pip install -r {}'.format(prod))
