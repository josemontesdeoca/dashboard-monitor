# !/usr/bin/env bash

set -ue

echo -e "\n*** Rolling back pending updates ***\n"
appcfg.py --oauth2 $* rollback .

echo -e "\n*** DEPLOYING THE APPLICATION ***\n"
appcfg.py --oauth2 $* update .
