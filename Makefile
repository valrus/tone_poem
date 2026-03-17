# Update version whenever any python file changes
VERSION.txt: $(shell find src/tone_poem -name '*.py' | sed 's~ ~\\ ~g')
	echo "$$(date "+%Y%m%d%H%M")" > $@

.PHONY: version
version: VERSION.txt
	sed -i "s/^version = \".*\"$$/version = \"0.0.1-$$(cat VERSION.txt)\"/" pyproject.toml

.PHONY: build
build: version
	direnv reload

.PHONY: run
run: build
	tone-poem

test: build
	pytest
