import requests
import json
import re

try: 
	token = os.getenv("MAILCHIMP_USERNAME")
	token = os.getenv("MAILCHIMP_KEY")
except:
	logger.info(str(datetime.datetime.now()) + " [ERROR] mailchimp environment variables not found. Exiting...")
	exit(1)

headers = {'Content-Type': 'application/json'}

# Members list URL
roster = "https://us19.api.mailchimp.com/3.0/lists/20eac59371"
members = "https://us19.api.mailchimp.com/3.0/lists/20eac59371/members"

# New member info
email = "test@unf.edu"
first_name = "test"
last_name = "api"

def subscribe(email, first_name, last_name):
	email = email + "@unf.edu"
	# print(email + " " + first_name + " " + last_name)
	data = {
		'email_address':email,
		'status':'subscribed',
		'merge_fields':{
			'FNAME':first_name,
			'LNAME':last_name
		}
	}

	resp = requests.post(members, auth=auth, headers=headers, json=data)
	#print(str(resp))
	if re.search(r'200', str(resp)):
		with open("log.txt", "a") as log:
			print("[SUCCESS] new member successfully added to email list")
			log.write("[SUCCESS] new member successfully added to email list\n")
		email_list_message = "[SUCCESS] new member successfully added to email list " + str(resp)
	elif re.search(r'400', str(resp)):
		with open("log.txt", "a") as log:
			print("[!!!] new member is already in the email list")
			log.write("[!!!] new member is already in the email list\n")
		email_list_message = "[!!!] new member is already in the email list " + str(resp)
	else:
		with open("log.txt", "a") as log:
			print("[ERROR] problem adding new member to email list")
			log.write("[ERROR] problem adding new member to email list\n")
		email_list_message = "[ERROR] problem adding new member to email list " + str(resp)
	return email_list_message


	#print(json.dumps(json.loads(resp.text), indent=4))


