#!/bin/bash
count=0
while IFS= read -r line; do
    curl -H "x-api-key: <your api key>" "https://api.wappalyzer.com/v2/lookup/?urls=$line" > technologies/$count.json
    ((count+=1))
done < "sites.csv"
