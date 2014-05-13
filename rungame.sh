#!/bin/bash
if [ $1 ]; then
	./bin/bzrflag --window-size=1450x725 --red-port=35000 --blue-port=35001 --green-port=35002 --purple-port=35003 --default-true-positive=$1 --default-true-negative=$2 --occgrid-width=100 --no-report-obstacles

else
	./bin/bzrflag --window-size=1450x725 --red-port=35000 --blue-port=35001 --green-port=35002 --purple-port=35003
fi
