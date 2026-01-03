# Backend Scripts

This directory contains principled data pipelines (PDPs) to distribute datasets. 

## academic-research-groups

This project annotate a given set of faculties on whether they have a research group or not and their openAlex database identifier. At the moment, the set of faculties are restricted to UVM faculties present on the November 2023 UVM payroll.

## scisciDB

This project seeks to streamline different sources of data to do science of science studies; namely openAlex and the semantic scholar database. We download snapshots of each database, manage updates, sync them, and derive new fields using ducklake. The goal is to offer what is missing from one or the other, not to replace them.

In the fastAPI x postgreSQL, we provide endpoints to do some analytics; essentially counting over time or fields. 
