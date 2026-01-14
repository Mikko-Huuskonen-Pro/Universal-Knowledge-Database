PYTHON ?= python

.PHONY: lint test demo

lint:
	$(PYTHON) -m ruff src tests

test:
	$(PYTHON) -m pytest

demo:
	@echo "Cleaning previous demo artifacts..."
	-powershell -Command "Remove-Item -Recurse -Force tmp-pack.ukdb,tmp-input,tmp-built.ukdb -ErrorAction SilentlyContinue"
	@echo "Creating demo input directory..."
	-powershell -Command "New-Item -ItemType Directory tmp-input | Out-Null; Set-Content tmp-input\\demo.txt 'hello from demo'"
	@echo "Running: ukdb init tmp-pack"
	@./ukdb.cmd init tmp-pack
	@echo "Running: ukdb validate tmp-pack.ukdb"
	@./ukdb.cmd validate tmp-pack.ukdb
	@echo "Running: ukdb build tmp-input tmp-built"
	@./ukdb.cmd build tmp-input tmp-built
	@echo "Running: ukdb validate tmp-built.ukdb"
	@./ukdb.cmd validate tmp-built.ukdb
	@echo "Running: ukdb hash tmp-built.ukdb"
	@./ukdb.cmd hash tmp-built.ukdb
	@echo "Running: ukdb validate tmp-built.ukdb (after hashing)"
	@./ukdb.cmd validate tmp-built.ukdb

