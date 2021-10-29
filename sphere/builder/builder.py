import os
import shutil
import argparse


def createPacs():
    """ Create the PACS"""

    parser = argparse.ArgumentParser()
    parser.add_argument('dirpath', help='Directory Path of created PACS')
    parser.add_argument(
        '-f', '--force', action='store_true',
        help='Force PACS folder remove if already exist')
    parser.add_argument('-env', '--envpath', help='PACS target IP')

    args = parser.parse_args()
    dirpath = args.dirpath
    envpath = args.envpath
    force = args.force

    try:
        if force:
            shutil.rmtree(os.path.join(dirpath))
    except Exception as e:
        print(e)

    os.makedirs(dirpath)

    path_file = os.path.realpath(__file__)
    path_builder = os.path.dirname(path_file)
    path_sphere = os.path.dirname(path_builder)

    # copy __init_.py and renamed version_pacs.py
    src_dir = os.path.join(path_sphere, '__init__.py')
    dst_dir = os.path.join(dirpath, 'version_pacs.py')
    shutil.copy2(src_dir, dst_dir)

    # Copy all files in setup_models
    models = os.path.join(path_builder, 'setup_models')

    # Copy mange.py
    shutil.copy2(os.path.join(models, 'manage.py'), dirpath)

    shutil.copytree(os.path.join(models, 'app'), os.path.join(dirpath, 'app'))

    if envpath:
        os.system(
            'ln -s ' + envpath + ' ' + os.path.join(dirpath, 'env_sphere'))


if __name__ == '__main__':
    createPacs()
