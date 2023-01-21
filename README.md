# Seenya


TLDR >> Seenya is a tool to detect wireless device mac addresses and log/report on them if they have been seen before.

Im not a coder, so dont expect too much but feel free to throw suggestions around


# Roadmap

1. Research the wireless capture card and its capabilities to ensure it can be used to create a wireless access point and capture MAC addresses of connected devices.

2. Set up the wireless capture card on your laptop and test its functionality by creating a wireless access point and connecting to it with a test device.

3. Write the script to create a wireless access point using the wireless capture card and beacon out to nearby cellular phones.

4. Develop a mechanism to capture the MAC addresses of connected devices, and save them to a log file.

5. Test the script by running it and verifying that it is able to create a wireless access point, beacon to nearby cellular phones, and capture and save their MAC addresses to a log file.

6. Optimize and refine the script as needed to improve performance and reliability.

7. Add any additional features or functionality as desired.


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
