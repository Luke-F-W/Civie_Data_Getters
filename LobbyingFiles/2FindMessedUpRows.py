"""
on a small amount of rows sometimes a cell in a column
gets split into multiple cells despite needing
to be in 1 cell, these require manual cleaning.
This short script prints which rows require 
cleaning by going through each row and seeing 
if column T or U have data in them, or if column D
(Date Published) isn't a valid "/"-delimited date,
if so it prints that row.
"""
import csv
import os

file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
filepathabove = os.path.dirname(filepath)
maincsv = os.path.join(filepathabove, "maincsv.csv") #csv to find the messed up rows in

with open(maincsv, 'r', encoding='utf-8') as csvv:
    x = 0
    for row in csv.reader(csvv):
        if len(row) > 3:
            d = row[3]
        else:
            d = ""
        if len(row) > 19:
            t = row[19]
        else:
            t = ''
        if len(row) > 20:
            u = row[20]
        else:
            u = ''

        # Date Published needs at least 3 "/"-separated parts,
        # otherwise fixdate()'s date.split("/")[1] or [2] throws IndexError
        bad_date = (not d) or (len(d.split("/")) < 3)

        if t or u or bad_date:
            print(x, "| Date Published:", repr(d))
        x += 1