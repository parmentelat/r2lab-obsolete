PUBLISH_PATH = /var/www/r2lab.inria.fr

EXCLUDES = .git

RSYNC-EXCLUDES = $(foreach exc,$(EXCLUDES), --exclude $(exc))

########## contents
publish:
	rsync -av $(RSYNC-EXCLUDES) --delete --delete-excluded ./ $(PUBLISH_PATH)/

install: publish

.PHONY: publish install
