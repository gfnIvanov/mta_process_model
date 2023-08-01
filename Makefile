.PHONY: install build lint

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
RUN = poetry run
REPRO = dvc repro

ifeq (,$(shell which poetry))
	HAS_POETRY=False
else
	HAS_POETRY=True
endif

check-poetry:
ifeq (False,$(HAS_POETRY))
	$(error Please use Poetry)
endif


#################################################################################
# SERVICE COMMANDS                                                              #
#################################################################################

## Install Python Dependencies
install: check-poetry
	poetry install

## Build with setup.py
build: check-poetry
	poetry build

## Lint using flake8
lint:
	flake8 src

# Check types
check-types:
	$(RUN) mypy .

## Pre-commit all files
prec-all:
	pre-commit run --all-files


#################################################################################
# MODELS COMMANDS                                                               #
#################################################################################

# use native models (without additional training)

# example: make use-gpt-native size="medium" text="пациент жалуется на повышенную"
use-gpt-native: check-poetry
ifeq (,$(size))
	$(RUN) use_gpt_native "$(text)"
else
	$(RUN) use_gpt_native "--size=$(size)" "$(text)"
endif

# example: make use-bert-native text="пациент жалуется на повышенную"
use-bert-native: check-poetry
	$(RUN) use_bert_native "$(text)"


#################################################################################
# PREPARE DATA                                                                  #
#################################################################################

parse-xml: check-poetry
	$(REPRO) -f -s genetics_to_yaml_file

depers: check-poetry
	$(REPRO) -f -s depers_genetics

del-dep-file:
	$(shell if [ -f "$(path)" ] ; then rm $(path); fi)

#################################################################################
# LOGS                                                                          #
#################################################################################

# show data logs: make data-logs str=50
data-logs:
ifeq (,$(str))
	tail $(PROJECT_DIR)/logs/data_logs.log
else
	tail -n $(str) $(PROJECT_DIR)/logs/data_logs.log
endif
