.PHONY: install build lint

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
CMD = poetry run

ifeq (,$(shell which poetry))
	HAS_POETRY=False
else
	HAS_POETRY=True
endif

check_poetry:
ifeq (False,$(HAS_POETRY))
	$(error Please use Poetry)
endif


#################################################################################
# SERVICE COMMANDS                                                              #
#################################################################################

## Install Python Dependencies
install: check_poetry
	poetry install

## Build with setup.py
build: check_poetry
	poetry build

## Lint using flake8
lint:
	flake8 src

## Pre-commit all files
prec-all:
	pre-commit run --all-files


#################################################################################
# MODELS COMMANDS                                                               #
#################################################################################

# use native models (without additional training)

# example: make use_gpt_native size="medium" text="пациент жалуется на повышенную"
use_gpt_native: check_poetry
ifeq (,$(size))
	$(CMD) use_gpt_native "$(text)"
else
	$(CMD) use_gpt_native "--size=$(size)" "$(text)"
endif

# example: make use_bert_native text="пациент жалуется на повышенную"
use_bert_native: check_poetry
	$(CMD) use_bert_native "$(text)"


#################################################################################
# PREPARE DATA                                                                  #
#################################################################################

parse_xml: check_poetry
	dvc repro genetics_to_yaml_file
