# Seenya


TLDR >> Seenya is a tool to detect wireless device mac addresses  and log/report on them if they have been seen before.

Im not a coder, so dont expect too much but feel free to throw suggestions around


# Roadmap

1. Sequence of functions (The technical steps and functions drawn out)
2. Foundational structures of code
3. Functioning backend (program should be function via cli at this point)
4. TBD 


# What Seenya is built on

The current plan is for Seenya to be run as python cli, with future GUI plans.
Seenya additionaly will be open source and remain that  way.


# Is Seenya currently functional in any way?

No


# Okay but what is  Seenya tho?

Seenya is an attempt at a python based script/program that utilizes the
aircrack-ng suite to gather MAC addresses of phones or smartwatches that
come into range of your wireless AP/wireless card. As the MAC comes into
range, the script will save the MAC of the device to a file and check if
it already exists, if yes, create an alert of some kind.
