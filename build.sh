#!/usr/bin/env bash
pip install pipenv
pipenv run pipenv install
python website/manage.py collectstatic --no-input
python website/manage.py makemigrations
python website/manage.py migrate
