from setuptools import setup, find_packages

setup(
    name='departamentos',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Babel',
        'Flask-Script',
    ]
)
