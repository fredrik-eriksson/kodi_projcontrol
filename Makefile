ADDON_NAME := $(shell grep '<addon id="' addon.xml |cut -d\" -f2)
VERSION := $(shell grep '  version=' addon.xml |cut -d\" -f2)
FILES = addon.xml service.py lib resources changelog.txt LICENSE
REPO_PLUGINS ?= ../repo-plugins
RELEASE_BRANCH ?= krypton

all: dist

dist:
	mkdir -p plugin.$(ADDON_NAME)
	cp -r $(FILES) plugin.$(ADDON_NAME)/
	zip -r plugin.$(ADDON_NAME)-$(VERSION).zip plugin.$(ADDON_NAME)/ \
		--exclude \*.pyc
	rm -r plugin.$(ADDON_NAME)

prepare_release:
	[ -d "$(REPO_PLUGINS)" ] || \
		git clone https://github.com/xbmc/repo-scripts "$(REPO_PLUGINS)"
	git -C $(REPO_PLUGINS) stash
	git -C $(REPO_PLUGINS) checkout $(RELEASE_BRANCH)
	rm -rf $(REPO_PLUGINS)/plugin.$(ADDON_NAME)
	mkdir $(REPO_PLUGINS)/plugin.$(ADDON_NAME)
	cp -r $(FILES) $(REPO_PLUGINS)/plugin.$(ADDON_NAME)/

clean:
	rm *.zip
