#!/usr/bin/python3
import discord
from discord.ext import commands
import re
import subprocess
import os
import asyncio
import mailchimp
import datetime

# grab user n#
unf_id = input("please enter unf id: ")

### grab api information for mailchimp/discord if no config file given give error msg ###
# 
# ***config file contents will be read in assuming the file format below:***
# if information is not presented in this order, bot wont work
#    
# [discord api key]
# [mailchimp api key]
# [mailchimp username]
#
# #

try:
	config_file = open('config.txt', 'r')
	file_contents = config_file.readlines()
	config_file.close()
	token = file_contents[0].strip()
except:
	print("[ERROR] no config file found. Exiting..")


cmd_prefix = ("?", "!")

client = commands.Bot(command_prefix="!")

print('my name is OSEC-bot and im here to fuck shit up'.format(client))
print(discord.__version__)

## Member join ##
# when new member joings server, log it into log file 
@client.event
async def on_member_join(member):
	print("\n----------------------------------------------------------------\n")
	print("New member joined: {}".format(member))
	with open("log.txt", "a") as log:
		time = str(datetime.datetime.now())
		log.write("----------------------------------------------------------------\n")
		log.write(time + " New member joined: {}\n".format(member))
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

	# set talon role id
	talon_role = discord.utils.get(message.guild.roles, name="Talon")

	# log join request message
	message_log = str(str(message.author) + ": " + message.content)

	# success/failure messages
	success_msg = "Welcome to OSEC " + message.author.mention
	failure_msg = "invalid N number " + message.author.mention

	# current time
	time = str(datetime.datetime.now())
	
	print("\n----------------------------------------------------------------\n")
	print("@{} user sent a message. (id: {})".format(message.author, message.author.id))
	print("validating new member... @{}".format(message.author))
	
	# log join-request message
	with open("log.txt", "a") as log:
		log.write("----------------------------------------------------------------\n")
		log.write(time + " @{} user sent a message.\n".format(message.author))
		log.write(time + " validating new member... @{}\n".format(message.author))

	await log_channel.send("-------------------------------------------------")	
	await log_channel.send("**validating new member... @{}**".format(message.author))

	# Grab N# from join-request message
	reg = re.findall(r'(n\d{8})', message.content, re.IGNORECASE)

	# if an n# is found, check if its found in the UNF AD
	if reg:
		# Grab user student id 
		student_id = reg[0]

		# Use ssh key to circumvent the password prompt from osprey server
		lookup = subprocess.run(['ssh', '-i','~/.ssh/osprey-key', 'n01177471@osprey.unf.edu', 'getent', 'passwd', student_id], stdout=subprocess.PIPE).stdout.decode('utf-8')
		print(lookup)

		# Student group = 100
		# Faculty group = 
		# Staff group = 102
		# login-name:password:userid:groupid:full name:home dir:login shell
		# Ex. -> n12345678:*:5070:100:firstname lastname:home/71/n12345678:/bin/bash

		# Match successful output from getent query
		lookup_result = re.match(r'(n\d{8}):(\*):(\d{3,5}):(\d{3}):([a-z]+)\s+([a-z\-\'\`]+):(\/[a-z]+\/\d{2}\/n\d{8}):(\/[a-z]+\/[a-z]+)', lookup, re.IGNORECASE)
		
		# if N# is invalid (did getent return a valid response?)
		if lookup_result is None:
			with open("log.txt", "a") as log:
				time = str(datetime.datetime.now())
				log.write(time + " " + message_log + " [ERROR] invalid N#\n")

			await log_channel.send("```" + message_log + "```" + " [ERROR] invalid N#")	

			print("[ERROR] invalid N#")

			error_msg = await message.channel.send("[ERROR] invalid N# " + message.author.mention)

			await asyncio.sleep(15)

			await message.delete()
			await error_msg.delete()
			return
		else:
			# Grab the groupid from getent output
			groupid = int(lookup_result.group(4))
			print("groupid: " + str(groupid))

		# Check if user is a member of student or staff group
		if groupid == 100 or groupid == 102:
			# Grab N# and name from the getent output (Thats all the data we need)
			student_id = lookup_result.group(1)
			first_name = lookup_result.group(5)
			last_name = lookup_result.group(6)
			student_info = student_id + " " + first_name + " " + last_name
			print(student_info)
			time = str(datetime.datetime.now())
			# await log_channel.send("@{}: ".format(message.author) + student_info)
			is_valid = True
		# new member is part of faculty
		else:
			with open("log.txt", "a") as log:
				time = str(datetime.datetime.now())
				log.write(time + " " + message_log + " [ERROR] faculty member detected\n")

			await log_channel.send("```" + message_log + "```" + " [ERROR] faculty member detected")	
			
			print("[ERROR] faculty member detected...")
			error_msg = await message.channel.send("[ERROR] this n# is not associated with a UNF student account " + message.author.mention)
			await message.author.send("We are unable to verify your status as a UNF student, if you are a faculty member interested in joining OSEC please contact one of the club officers for further information. We apologize for the inconvenience.")
			await asyncio.sleep(15)
			await message.delete()
			await error_msg.delete()
			return

		# is the N# provided associated with a valid student account?
		if is_valid:
			with open("log.txt", "a") as log:
				time = str(datetime.datetime.now())
				log.write(time + " " + message_log + " [SUCCESS] new member is a valid UNF student\n")
				log.write(time + " New OSEC member: " + student_id + " " + first_name + " " + last_name + "\n")

			await log_channel.send("```" + message_log + "```" + " [SUCCESS] new member is a valid UNF student")
			
			print("[SUCCESS] new member is a valid UNF student")

			# assign talon role
			await message.author.add_roles(talon_role)
			
			# Send bot response message
			success_response = await message.channel.send(success_msg)

			# Log student info 
			print("New OSEC member: " + student_id + " " + first_name + " " + last_name)

			# add user to mailchimp subscription list
			mailchimp_msg = mailchimp.subscribe(student_id, first_name, last_name)
			await log_channel.send(mailchimp_msg)

			# STEADY LADS
			await asyncio.sleep(15)

			# Delete original join-request message
			await message.delete()
			print("join request message has been deleted")

			# Delete bot response message
			await success_response.delete()
			print("bot response message deleted")
			return
		else:
			print("[FAILURE] new member is not a valid UNF student")
			await log_channel.send("[FAILURE] new member is not a valid UNF student")	
			failure_response = await message.channel.send(failure_msg)
			await asyncio.sleep(15)
			# Delete bot response message
			await failure_response.delete()
			return
	else:
		with open("log.txt", "a") as log:
				time = str(datetime.datetime.now())
				log.write(time + " " + message_log + " [ERROR] invalid input\n")
		await log_channel.send("```" + message_log + "```" + " [ERROR] invalid input")
		print("[ERROR] invalid input")
		error_msg = await message.channel.send("[ERROR] invalid input")
		await asyncio.sleep(15)
		await message.delete()
		await error_msg.delete()
		return

client.run(token)
