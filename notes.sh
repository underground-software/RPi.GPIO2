#!/bin/bash

# View repository notes and todos

for target in $(cat notes_targets)
do

	echo "$target"
	grep -rnw NOTE $target
	grep -rnw TODO $target
	grep -rnw FIXME $target
done

exit 0
