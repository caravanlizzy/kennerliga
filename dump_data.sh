#!/bin/bash

for app in 'user' 'season' 'league' 'match_result'
do
  ./manage.py dumpdata $app > $app/fixtures/sample_data.json
done