#!/bin/bash

curl -s "https://www.amfiindia.com/spages/NAVAll.txt" -o NAVAll.txt

outfile="nav_data.tsv"
echo -e "Scheme Name\tAsset Value" > "$outfile"

tail -n +1 NAVAll.txt | awk -F ';' 'NF >= 5 && $4 != "" && $5 != "" { print $4 "\t" $5 }' >> "$outfile"

echo "Done. Saved to $outfile"
