from setuptools import setup, find_packages

setup(
    name='Concierge',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'SQLAlchemy',
        'WTForms',
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Flask-Testing',
        'Flask-DebugToolbar'
    ]
)
