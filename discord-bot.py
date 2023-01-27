import discord
from discord.ext import commands
import re
import subprocess
import os
import asyncio
#import mailchimp
import datetime
import os.path
import sys
import requests
import logging
from enum import Enum

### grab api information for mailchimp/discord if no config file given give error msg ###

"""
config file contents will be read in assuming the file format below:

NOTE: if information is not presented in this order, bot wont work

[discord api key]
[mailchimp api key]
[mailchimp username]
"""

handler = logging.FileHandler(filename="log.txt", mode="a")
logger = logging.getLogger("Custom")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# check for config file
try:
	config_file = open('config.txt', 'r')
	file_contents = config_file.readlines()
	config_file.close()
	token = file_contents[0].strip()
except:
	logger.info(str(datetime.datetime.now()) + " [ERROR] no config file found. Exiting...")
	exit()

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)


class StudentResult(Enum):
	NOT_FOUND = 0
	STUDENT = 1
	FACULTY = 2

def is_student(n_number):
	user_url = "https://login.microsoftonline.com/common/GetCredentialType"
	faculty_url = "https://webapps.unf.edu/faculty/bio/api/v1/faculty?searchLimit=1&searchTerm="
	user_response = requests.post(user_url, json={"username": f"{n_number}@unf.edu"}).json()

	is_valid_user = user_response["IfExistsResult"] == 0
	if not is_valid_user:
		return StudentResult.NOT_FOUND
	faculty_response = requests.get(f"{faculty_url}{n_number}").json()
	if (len(faculty_response["payload"]) > 0) and (faculty_response["payload"][0]["isFaculty"] == True):
		return StudentResult.FACULTY
	return StudentResult.STUDENT


## Member join ##
# when new member joings server, log it into log file 
@client.event
async def on_member_join(member):
	
	# get Talon role id
	new_member_role = discord.utils.get(message.guild.roles, name="Talon")
	
	# assign "Talon" role
	await member.add_roles(new_member_role)

	logger.info("----------------------------------------------------------------")
	logger.info(str(datetime.datetime.now()) + " New member joined: {}".format(member))
	return


# join-requests
@client.event
async def on_message(message):
	# Only read messages from "join-requests" channel
	if str(message.channel) != "join-requests":
		return

	# If the message is from the bot exit
	if message.author == client.user:
		return

	# set bot logging channel
	log_channel = await client.fetch_channel("623862015781502976")

	# set Security Intern role id
	member_role = discord.utils.get(message.guild.roles, name="Security Intern")

	# log join request message
	message_log = str(str(message.author) + ": " + message.content)

	# success/failure messages
	success_msg = "Welcome to OSEC " + message.author.mention
	failure_msg = "invalid N number " + message.author.mention
	
	# log join-request message
	logger.info("----------------------------------------------------------------")
	logger.info(str(datetime.datetime.now()) + " @{} user sent a message.".format(message.author))
	logger.info(str(datetime.datetime.now()) + " validating new member... @{}".format(message.author))

	await log_channel.send("-------------------------------------------------")	
	await log_channel.send("**validating new member... @{}**".format(message.author))

	# Grab N# from join-request message
	reg = re.findall(r'(n\d{8})', message.content, re.IGNORECASE)
	if reg:
		student_id = reg[0]
	else:
		logger.error(str(datetime.datetime.now()) + " " + message_log + " [ERROR] invalid input")
		await log_channel.send("```" + message_log + "```" + " [ERROR] invalid input")

		error_msg = await message.channel.send("[ERROR] invalid input")
		await asyncio.sleep(15)
		await message.delete()
		await error_msg.delete()
		return
		
	student_check = is_student(student_id)

	if student_check == StudentResult.STUDENT:
		# verification success
		logger.info(str(datetime.datetime.now()) + " " + message_log + " [SUCCESS] new member is a valid UNF student")
		logger.info(str(datetime.datetime.now()) + " New OSEC member: " + student_id)

		await log_channel.send("```" + message_log + "```" + " [SUCCESS] new member is a valid UNF student")

		# assign "Security Intern" role
		await message.author.add_roles(member_role)

		# Send bot response message
		success_response = await message.channel.send(success_msg)

		# Log student info
		logger.info(str(datetime.datetime.now()) + " New OSEC member: " + student_id)

		# add user to mailchimp subscription list
		#mailchimp_msg = mailchimp.subscribe(student_id, first_name, last_name)
		#await log_channel.send(mailchimp_msg)

		# STEADY LADS
		await asyncio.sleep(15)

		# Delete original join-request message
		await message.delete()
		logger.info(str(datetime.datetime.now()) + " join request message has been deleted")

		# Delete bot response message
		await success_response.delete()
		logger.info(str(datetime.datetime.now()) + " bot response message deleted")

		return
	elif student_check == StudentResult.FACULTY:
		# faculty member
		logger.error(str(datetime.datetime.now()) + " " + message_log + " [ERROR] faculty member detected")

		await log_channel.send("```" + message_log + "```" + " [ERROR] faculty member detected")	

		error_msg = await message.channel.send("[ERROR] this n# is not associated with a UNF student account " + message.author.mention)
		await message.author.send("We are unable to verify your status as a UNF student, if you are a faculty member interested in joining OSEC please contact one of the club officers for further information. We apologize for the inconvenience.")
		await asyncio.sleep(15)
		await message.delete()
		await error_msg.delete()
		return

	elif student_check == StudentResult.NOT_FOUND:
		logger.warning(str(datetime.datetime.now()) + " [FAILURE] new member is not a valid UNF student")
		await log_channel.send("[FAILURE] new member is not a valid UNF student")	
		failure_response = await message.channel.send(failure_msg)
		await asyncio.sleep(15)
		# Delete bot response message
		await failure_response.delete()
		return


logger.info("Discord.py version " + discord.__version__)
client.run(token, log_handler=handler)

