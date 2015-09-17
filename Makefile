tests: unit_tests lint;
unit_tests:
	nosetests --with-coverage --cover-erase --cover-package=bashql --cover-html

lint:
	flake8 bashql
	flake8 tests

cloc:
	cloc . --exclude-dir=env,cover,htmlcov
