#!/bin/bash
if [ $1 ]; then

./bin/bzrflag --window-size=1450x725 --green-port=35000 --red-port=35001 --world=maps/fourls2p.bzw --default-posnoise=3 --friendly-fire --respawn-time=240 --max-shots=3 --default-tanks=10 --default-true-positive=.97 --default-true-negative=.9 --occgrid-width=100 --no-report-obstacles

else

./bin/bzrflag --window-size=1450x725 --green-port=45000 --red-port=45001 --world=maps/fourls2p.bzw --default-posnoise=3 --friendly-fire --respawn-time=240 --max-shots=3 --default-tanks=10 --default-true-positive=.97 --default-true-negative=.9 --occgrid-width=100 --no-report-obstacles
fi
