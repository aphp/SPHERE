# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sphere

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

REQUIRES = [
    "colorlog==4.0.2",
    "dirsync==2.2.4",
    "psutil==5.6.7",
    "psycopg2-binary>=2.8.4",
    "pydicom==2.1.2",
    "pynetdicom==1.5.5",
    "PyYAML==5.3",
    "six==1.13.0",
    "SQLAlchemy==1.3.13",
    "sqlalchemy-views==0.2.4",
    "requests==2.23.0",
    "django==3.0.2",
    "djangorestframework==3.11.0",
    "drf-yasg==1.17.1",
    "pylibjpeg==1.3.0",
    "pylibjpeg-libjpeg==1.2.0",
    "pylibjpeg-rle==1.1.0",
    "pylibjpeg-openjpeg==1.1.1"
    ]

CLASSIFIERS = [
            "Development Status :: 4 - Beta",
            "License :: OSI Approved",
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Topic :: Medical Science Apps",
        ]

setup(
    name='sphere',
    version=sphere.__version__,
    description='Sample package for Python-Guide.org',
    long_description=readme,
    author='Aurélien Maire, Ossama Achouri, Cyrina Saussol, Amael CHAIGNEAU',
    author_email='aurelien.maire@aphp.fr, ossama_achouri@yahoo.fr, '
                'cyrina.saussol@aphp.fr, amael.chaigneau-ext@aphp.fr',
    # url='https://github.com/kennethreitz/samplemod',
    keywords=['dicom', 'pydicom'],
    install_requires=REQUIRES,
    license=license,
    packages=find_packages(),
    include_package_data=True,
    classifiers=CLASSIFIERS,
    scripts=['scripts/sphere-admin'],
    entry_points={'console_scripts': [
        'sphere-admin = sphere.builder.builder:createPacs',
    ]},
    platforms='ALL',
    python_requires='>=3.6.1',
)
