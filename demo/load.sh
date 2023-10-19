#!/bin/sh
file="$1"
while IFS= read -r line; do 
curl -H "Content-Type: application/json" -d "$line" http://localhost:3000/submit
done < "$file"
