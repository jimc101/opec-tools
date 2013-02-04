from subprocess import call

call('rm -rf dist')
call('python setup.py bdist_egg')
call('easy_install dist/opec-0.1-py3.2.egg')
