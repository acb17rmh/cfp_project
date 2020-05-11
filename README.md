# cfp_project

> A final year dissertation project exploring the extraction of information from 'Call for Papers' emails. 

## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)

---

## Installation

- Clone this repo to your local machine using `git clone https://github.com/acb17rmh/cfp_project`
- Install the required dependencies: `pip install -r requirements.txt`

---

## Features

- Classify a set of emails, labelling them as CFPs or non-CFPs
- Extract the following information from a set of CFPs: conference name, location, start date, submission deadline,
  notification due date and final version deadline.
  
---

## Usage

- To train the classifier on the corpus and evaluate performance: `python cfp_classifier.py`
- To run the extraction system: `python extract.py -i INPUTFILENAME -o OUTPUTFILENAME`
- To run the evaluation system: `python evaluate.py -i INPUTFILENAME`
 