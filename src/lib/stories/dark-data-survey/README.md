# Dark-data-survey 

This is a experimental project in that we 
1. Ask people survey questions that we record 
2. Work with sensitive data. 

Lets talk about each independently.

### Participatory visual essays

When asking people survey questions is one of the few cases where we need server-side logic (hence, a node server app or else). For each user, we will be updating dynamically our database with users' feedback, in turn updating our data essays with the data.

We use fingerprinting to distinguish between users.

In the process, we also use modern tools and custom types to work with survey data. The idea is that those techniques can help us manage complexity arising naturally from conducting surveys.

To manage that complexity, we use:

- a sqlite3 database on the frontend to record the data... this could be replaced by our postegresql backend.