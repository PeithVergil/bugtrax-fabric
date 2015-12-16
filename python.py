from fabric.api import cd, env, put, run, task, sudo, prefix, require
from fabric.contrib import files

import utils


@task
def conda_install():
    """
    Download and install "miniconda".

    :Example:

    fab --config=config.conf python.conda_install
    """
    require('MINICONDA_NAME')
    require('MINICONDA_FILE')

    with cd(utils.home()):
        if not files.exists(env.MINICONDA_NAME):
            # Download the miniconda installer.
            run('wget {0}'.format(env.MINICONDA_FILE))

        # Give permission to execute installer.
        run('chmod u+x {0}'.format(env.MINICONDA_NAME))

        # Put miniconda in the "apps" directory.
        apps = utils.home('apps')

        run('mkdir -p {0}'.format(apps))

        # OPTIONS:
        #
        # -b Run in silent mode.
        # -p The path where miniconda will be installed.
        run('bash {0} -b -p {1}/miniconda'.format(env.MINICONDA_NAME, apps))

        # Add the executables to the system path.
        export = 'export PATH="{0}/miniconda/bin:$PATH"'.format(apps)

        files.append('.bashrc', '###########')
        files.append('.bashrc', '# MINICONDA')
        files.append('.bashrc', export)

        # Remove the installer after installation.
        run('rm {0}'.format(env.MINICONDA_NAME))


@task
def conda_list_environments():
    """
    List all conda virtual environments.

    :Example:

    fab --config=config.conf python.conda_list_environments
    """
    conda = '{0}/bin/conda'.format(utils.home('apps', 'miniconda'))

    run('{conda} info --envs'.format(conda=conda))


@task
def conda_create_environment(name, python='3'):
    """
    Create a new virtual environment. Installs "Python 3" by default.

    :Example:

    fab --config=config.conf python.conda_create_environment:name=bugtrax
    """
    conda = '{0}/bin/conda'.format(utils.home('apps', 'miniconda'))

    run('{conda} create --name {name} python={python} --yes'.format(
        name=name,
        conda=conda,
        python=python))


@task
def conda_install_requirements(venv):
    """
    Run "pip install -r" on the requirements file.

    :Example:

    fab --config=config.conf python.conda_install_requirements:venv=bugtrax
    """
    # Upload the requirements file.
    put(utils.files('requirements', 'base.txt'), utils.home('base.txt'))
    put(utils.files('requirements', 'prod.txt'), utils.home('prod.txt'))

    # Activate the virtual environment.
    activate = '{0}/bin/activate'.format(utils.home('apps', 'miniconda'))

    with prefix('source {activate} {venv}'.format(venv=venv, activate=activate)):
        run('pip install -r {0}'.format(utils.home('prod.txt')))

    # Remove the uploaded files.
    with cd(utils.home()):
        run('rm {0}'.format(utils.home('base.txt')))
        run('rm {0}'.format(utils.home('prod.txt')))


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
