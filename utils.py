import random
import string

from crypt import crypt
from hashlib import md5
from os.path import abspath, dirname, exists, join


# Use the system random generator.
rand = random.SystemRandom()


def random_string(length=30):
    choices = string.ascii_lowercase + string.ascii_uppercase

    return ''.join(rand.choice(choices) for _ in range(length))


def local_path(*filenames):
    return join((dirname(abspath(__file__))), *filenames)


def file_path(*filenames):
    path = local_path('files', *filenames)

    if exists(path):
        return path

    return None


def file_read(*filenames):
    result = None
    
    path = file_path(*filenames)

    if path:
        with open(path, 'r') as reader:
            result = reader.read()
    
    return result


def config(*filenames):
    path = local_path('config', *filenames)

    if exists(path):
        return path

    return None


def hash(password):
    # Create a random salt.
    salt = '$6${0}'.format(random_string(8))
    
    return crypt(password, salt)


def pghash(username, password):
    return 'md5' + md5(password + username).hexdigest()