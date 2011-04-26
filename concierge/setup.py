from setuptools import setup, find_packages

setup(
    name='Concierge',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'blinker',
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Flask-Script',
        'Flask-Testing',
        'Flask-DebugToolbar'
    ]
)
