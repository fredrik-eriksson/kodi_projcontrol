ADDON_NAME := $(shell grep '<addon id="' addon.xml |cut -d\" -f2)
VERSION := $(shell grep '  version=' addon.xml |cut -d\" -f2)
FILES = addon.xml icon* lib* LICENSE README.rst resources service.py
REPO_PLUGINS ?= ../repo-plugins
RELEASE_BRANCH ?= matrix

all: dist

dist:
	mkdir -p plugin.$(ADDON_NAME)
	cp -r $(FILES) plugin.$(ADDON_NAME)/
	zip -r plugin.$(ADDON_NAME)-$(VERSION).zip plugin.$(ADDON_NAME)/ \
		--exclude \*.pyc
	rm -r plugin.$(ADDON_NAME)

prepare_release:
	[ -d "$(REPO_PLUGINS)" ] || \
		git clone --depth 5 -b $(RELEASE_BRANCH) https://github.com/xbmc/repo-scripts "$(REPO_PLUGINS)"
	git -C $(REPO_PLUGINS) stash
	git -C $(REPO_PLUGINS) checkout $(RELEASE_BRANCH)
	rm -rf $(REPO_PLUGINS)/plugin.$(ADDON_NAME)
	mkdir $(REPO_PLUGINS)/plugin.$(ADDON_NAME)
	cp -r $(FILES) $(REPO_PLUGINS)/plugin.$(ADDON_NAME)/

clean:
	rm *.zip
