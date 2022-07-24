CC=pyinstaller
CFLAGS=-F 

channelbackup: channel-backup.py 
	pip install pip-autoremove poetry pyinstaller
	poetry export -f requirements.txt -o requirements.txt --without-hashes
	pip install -r requirements.txt
	$(CC) $(CFLAGS) channel-backup.py 

.PHONY: clean
clean:
	for line in $$(awk -F= '{print $$1}' requirements.txt); do $$(pip-autoremove -y $${line}); done
	pip-autoremove -y poetry pyinstaller
	pip uninstall -y pip-autoremove
	rm -rf build dist geckodriver.log .pytest_cache channel-backup.spec requirements.txt
