deploy_local_dev:
	sh $(CURDIR)/scripts/run_local_dev.sh

stop_local_dev:
	sh $(CURDIR)/scripts/stop_local_dev.sh

install_pep8:
	pip3 install flake8

validate_pep8:
	flake8 .. --exclude venv,.venv --show-source --statistic

remove_temporal_files:
	sh $(CURDIR)/scripts/remove_temporal_files.sh