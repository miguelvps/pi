from setuptools import setup, find_packages

setup(
    name='Servicos_Processuais',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Script',
    ]
)
