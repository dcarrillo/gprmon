# noxfile.py
import nox

nox.options.sessions = ['lint', 'typing']
locations = ['gprmon.py', 'GPRMon/']

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
