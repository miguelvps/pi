from setuptools import setup, find_packages

setup(
    name='geo',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Script',
    ]
)
