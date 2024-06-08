#!/bin/bash

for folder in 'game' 'season' 'league' 'result' 'user'
do
	rm -r $folder/migrations/00*
done
