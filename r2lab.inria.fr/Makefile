PUBLISH_PATH = /var/www/r2lab

EXCLUDES = .git

RSYNC-EXCLUDES = $(foreach exc,$(EXCLUDES), --exclude $(exc))

########## contents
publish:
	rsync -av $(RSYNC-EXCLUDES) --delete --delete-excluded ./ $(PUBLISH_PATH)/

install: publish

.PHONY: publish install
