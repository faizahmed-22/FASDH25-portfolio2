# input

#import libraries
import re
import os
import pandas as pd

#note down the tables needed from the .tsv file
def write_tsv(rows, column_list, path):
    df = pd.DataFrame(rows, columns=column_list)
    df.to_csv(path, sep="\t", index=False)

#setup paths
folder = '../articles'
gazetteer_path = '../gazetteers/geonames_gaza_selection.tsv'

#read gazetteer file
with open(gazetteer_path, encoding="utf-8") as file:
    data = file.read()

#create dictionary for regex
patterns = {}

#split the text into rows
rows = data.split("\n")

for row in rows[1:]:  # Skip header
    columns = row.split("\t")             # split each row by tab into columns
    asciiname = columns[0]                # name of places in the first column
    name_variants = [asciiname]
    alternate_names = columns[5].strip()  # check for alternate names if there are any

    if alternate_names:                         # under the condition that alternate names exist
      alternate_list = alternate_names.split(",")     # Split them by comma
      for name in alternate_list:
        name_variants.append(name.strip())      # add each to name_variants

    # new regex pattern for name variant
    regex_pattern = "|".join(re.escape(name) for name in name_variants)
    # store the regex pattern and count
    patterns[asciiname] = {"pattern": regex_pattern, "count": 0}

mentions_per_month = {}              # dictionary for mention of place per month
war_start_date = "2023-10-07"        # establish date to look out for

for filename in os.listdir(folder):             # loop through each file in the article folder
    date_str = filename.split("_")[0]           # look at the date from the filename
    if date_str < war_start_date:               # articles before the war start date are disregarded
        continue

    file_path = f"{folder}/{filename}"          # path to the article file
    with open(file_path, encoding="utf-8") as file:  #read the articles
        text = file.read()

    for place in patterns:                      # loop through gazetteer
        pattern = patterns[place]["pattern"]    # regex pattern for the current place
        matches = re.findall(pattern, text, re.IGNORECASE)  # find all matches
        count = len(matches)                    #  place mentions
        patterns[place]["count"] += count       # add up total count

        month_str = date_str[:7]                # extract both year and month

        if place not in mentions_per_month:     # under the condition place does not exist in dicitonary then add it
            mentions_per_month[place] = {}
        if month_str not in mentions_per_month[place]:
            mentions_per_month[place][month_str] = 0

        mentions_per_month[place][month_str] += count  #  count to the corresponding month

#Print Output
for place in mentions_per_month:                      # loop through each place
    print(f'"{place}": {{')
    month_list = list(mentions_per_month[place].keys())
    for month in month_list:                          # loop through each month
        count = mentions_per_month[place][month]      #  mention count
        if month != month_list[-1]:                   # if it's not the last month, print with a comma
            print(f'    "{month}": {count},')
        else:                                         #if in rhe last month, omit the comma
            print(f'    "{month}": {count}')
    print("},")

#Prepare Rows and Write TSV
output_rows = []                                      # create empty list to store output rows
for place in mentions_per_month:                      # loop through each place
    for month in mentions_per_month[place]:           # loop through each month for that place
        count = mentions_per_month[place][month]      # mention count
        output_rows.append((place, month, count))

write_tsv(output_rows, ["place", "month", "count"], "output.tsv")  # data to tsv file
#review the script
