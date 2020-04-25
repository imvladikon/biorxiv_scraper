Data mining project - second checkpoint
In this exercise you will wrap your scraper with a command line interface, and add to it the
ability to read and write to a database

Command line interface
1. Wrap up your web scraper to be able to call it with different arguments from the
terminal.
2. Use ​click​ or ​argparse​ packages.

Database implementation
1. Design an ERD for your data. Think about which fields should be primary and foreign
keys, and how you distinct new entries from already existing ones.
2. Take notice to primary and foreign keys.
3. Write a script that creates your database structure (python or sql), it should be separate
from the main scraper code (but should be part of the project and submitted as well).
4. Add to your scraper the ability to store the data it scrapes to the database you designed.
It should store only new data and avoid duplicates.

Good luck!