#!/usr/bin/env bash
poetry update
poetry lock
poetry check
poetry install --sync