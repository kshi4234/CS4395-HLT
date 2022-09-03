---
layout: default
title: Contact
permalink: /descriptions/
---

## Descriptions

### Assignment 1
In the first assignment I was tasked to take in a CSV file and reformat the data contained within the file. Each data entry consists of 5 fields which are: last name, first name, middle initial, identification number, and phone number. 

My program reads in the CSV file contents by line. Then it throws away the header and splits the remaining lines by the comma delimiters. Then it calls a method that begins entering the data to create a Person object (the Person class containing all relevant attributes in the CSV). Each setter method in the Person class checks for proper formatting; in some cases it is a simple correction (such as capitalizing names), while for ID there is more difficulty and so to correct an improperly formatted ID user input is required.

The program can be run through terminal by running the command 'python [NAME OF PROGRAM] [RELATIVE PATH TO data.csv]', or by typing 'python' and hitting enter to start a python session, then running '[NAME OF PROGRAM] [RELATIVE PATH TO data.csv]'.

In my opinion, Python is extremely powerful for text processing because of how easy it is to unpack values from an array or tuple. Furthermore, the String class in Python comes with useful methods like .split(), and regex is intuitive to use in Python. However, whenever I am trying to get numbers from processing text I sometimes forget to typecast the string into an integer. Normally it would be easy to catch where this occurs because other languages like Java and C++ have static typing, whereas in Python when I have typing issues I need to go sleuthing. Although this isn't a huge issue, cumulatively the time lost adds up.

For the most part, this project was a review in Python because I am already familiar with text processing and file I/O functionality in Python.


[<-- Back](https://kshi4234.github.io/CS4395-HLT/)
