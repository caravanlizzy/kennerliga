#!/bin/bash

for folder in 'game' 'season' 'league' 'result' 'user'
do
	rm -r $folder/migrations/000*
done
