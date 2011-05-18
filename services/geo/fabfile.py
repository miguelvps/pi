from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.console import confirm


env.user = 'root'
env.hosts = ['concierge.dyndns.org']

env.project = 'pes'
env.directory = '/home/pi/%(project)s/' % env # remote directory


def virtualenv(command):
    source = 'source %(directory)sENV/bin/activate && ' % env
    run(source + command)

def upload():
    local('tar ch . | gzip > %(project)s.tar.gz' % env)
    #local('git archive HEAD . | gzip > %(project)s.tar.gz' % env)
    put('%(project)s.tar.gz' % env, env.directory)
    local('rm %(project)s.tar.gz' % env)
    with cd(env.directory):
        run('tar xzf %(project)s.tar.gz' % env)
        run('rm %(project)s.tar.gz' % env)

def install():
    run('mkdir %(directory)s' % env)
    upload()
    with cd(env.directory):
        run('virtualenv --no-site-packages ENV')
        virtualenv('pip install -r requirements.txt')
        virtualenv('python setup.py develop')
        virtualenv('pip install gunicorn')
        virtualenv('python manager.py resetdb')
        virtualenv('python manager.py fixtures')

def uninstall():
    stop()
    run('rm -r %(directory)s' % env)

def start():
    with cd(env.directory):
        if exists('gunicorn.pid') and \
            not confirm("gunicorn.pid already exists. Continue anyway?"):
                abort("Aborting at user request.")
        virtualenv('gunicorn -c gunicorn.conf %(project)s.app:app' % env)

def stop():
    with cd(env.directory):
        if exists('gunicorn.pid'):
            run('kill -9 `cat gunicorn.pid`')
            run('rm gunicorn.pid')

def reload():
    with cd(env.directory):
        if exists('gunicorn.pid'):
            run('kill -HUP `cat gunicorn.pid`')
        else:
            start()

def update():
    upload()
    reload()

