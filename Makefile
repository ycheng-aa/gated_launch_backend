CHECK_DIRS=.
FLAKE8_CONFIG_DIR=tox.ini
TEST_PACAKGES=apps.task_manager.testcases.integration \
apps.common.testcases.integration \
apps.user_group.testcases.integration \
apps.strategy.testcases.integration \
apps.app.testcases.integration \
apps.auth.testcases.integration \
apps.info.testcases.integration \
apps.award.testcases.integration \
apps.usage.testcases.integration \
apps.issue.testcases.integration

CT_PACAKGES=apps.common.testcases.ct

.PHONY: docs

docs:
	make -C docs/ html

all_tests: flake8 test verify_migrations

all_dev_tests: flake8 dev_test verify_migrations

flake8:
	flake8 $(CHECK_DIRS) --config=$(FLAKE8_CONFIG_DIR)

# Local test, print the output to console without generate the xml test report
test:
	python3 manage.py test apps --settings gated_launch_backend.settings_runner

verify_migrations:
	python3 manage.py makemigrations --dry-run --check

dev_test: integration

# Testing Integration after deployment finished, and generate the xml test report
integration:
	python3 manage.py test -v 1 --settings gated_launch_backend.settings_test ${TEST_PACAKGES}

coverage:
	python3 manage.py test -v 1 --settings gated_launch_backend.settings_cover ${TEST_PACAKGES}

ct:
	python3 manage.py test -v 1 --settings gated_launch_backend.settings_test ${CT_PACAKGES}

