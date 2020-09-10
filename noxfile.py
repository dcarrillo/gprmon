# noxfile.py
import nox

nox.options.sessions = ['lint', 'typing', 'tests']
locations = ['gprmon.py', 'GPRMon/', 'tests/']

lint_common_args = ['--max-line-length', '120']
mypy_args = ['--ignore-missing-imports']


@nox.session()
def lint(session):
    args = session.posargs or locations
    session.install('pycodestyle', 'flake8', 'flake8-import-order')
    session.run('pycodestyle', *(lint_common_args + args))
    session.run('flake8', *(lint_common_args + args))


@nox.session()
def typing(session):
    args = session.posargs or locations
    session.install('mypy')
    session.run('mypy', *(mypy_args + args))


@nox.session()
def tests(session):
    session.install('pytest')
    session.install('-r', 'requirements.txt')
    session.run('pytest')
