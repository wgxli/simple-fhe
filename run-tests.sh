#!/bin/bash
coverage run --branch -m unittest discover tests
coverage html
