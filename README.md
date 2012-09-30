## Description

A proof of concept autonomous conversational agent for my honours project. 

## Requirements

To run this, your system has to satisfy the following requirements:
* Python >=2.7.2, but not 3
* Java Hotspot VM (Java 5 or above)
* BeautifulSoup 3.2.1
* foreman
* at least 512MB RAM to load the classifiers into memory

## Setup

1. Clone the project and `cd` into the project directory.
2. `mv .env.example .env` and change the file with your settings. 
3. Edit `identity.py` to add identities to the agent. 
4. `foreman start`


## Project structure

* `/classifiers` contains jar binaries for the Stanford MaxEnt and CRF classifiers.
* `/data` contains a serialization of the current state of the agent
* `/incoming` emails that will/have been processed
* `/misc` various notes on the classifiers which I don't want to forget
* `/models` contain models for the MaxEnt and CRF classifiers
* `/scenarios` the knowledge base of the agent
* `/scripts` various quick-and-dirty scripts that I have had to write at some point. Not recommended for reuse. 
* `.` contains the main components

## Main features

* Crawlers and parsers to automatically obtain new messages and responses
* Multiple agent identities
* Email threading
* Classifiers to recognize message type, main actors, etc.
* Sophisticated AI for response generation
* Metrics module
