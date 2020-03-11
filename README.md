<p align="center"> 
<img src="https://github.com/DLJ42/OSEC-bot/blob/master/osec_logo-discord_black.png">
</p>

# OSEC-bot
Discord bot built to verify members as *current* UNF students.

## Student Verification
upon joining the discord server, users are asked to submit their names and student id to a channel being monitored by the bot. Upon receiving the message, the bot login into a remote machine hosted by UNF and proceedingly check if the user information is found within the school's Active Directory.

## Bot Administration
Only authorized personel are permitted to run the bot. Without proper authorization, the bot *will not function*. If you are interested in becoming involved with OSEC, please contact one of the officers through the Discord server. 

## Usage
if authorized to run the bot on your machine, you will need to manually generate an ssh key for the remote server hosted by UNF in order to automate the verification process.

## Dependencies
* https://github.com/Rapptz/discord.py
* https://requests.readthedocs.io/en/master/

## OSEC Logo Credit
https://github.com/rothso/
