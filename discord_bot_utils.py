import logging
import datetime
from enum import Enum
import requests

handler = logging.FileHandler(filename="log.txt", mode="a")
logger = logging.getLogger("Custom")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class StudentResult(Enum):
    NOT_FOUND = 0
    STUDENT = 1
    FACULTY = 2


def is_student(n_number):
    user_url = "https://login.microsoftonline.com/common/getcredentialtype"
    faculty_url = "https://webapps.unf.edu/faculty/bio/api/v1/faculty?searchLimit=1&searchTerm="

    try:
        response = requests.post(user_url, json={"username": f"{n_number}@unf.edu"}, timeout=10)
        user_response = response.json()
        is_valid_user = user_response["IfExistsResult"] == 0

        response = requests.get(f"{faculty_url}{n_number}")
        faculty_response = response.json()

        if not is_valid_user:
            return StudentResult.NOT_FOUND
        else:
            if (len(faculty_response["payload"]) > 0) and (faculty_response["payload"][0]["isFaculty"] == True):
                logger.info(str(datetime.datetime.now()) + f"[INFO] {n_number} is faculty.")
                return StudentResult.FACULTY
            else:
                logger.info(str(datetime.datetime.now()) + f"[INFO] {n_number} is a student.")
                return StudentResult.STUDENT


    except Exception as err:
        logger.error(str(datetime.datetime.now()) + f"{err}")
        return StudentResult.NOT_FOUND

# try:
# 	response =	response.get(f"{faculty_url}{n_number}")
# 	faculty_response = response.json()
# except response.exceptions.HTTPError as err:
# 	logger.error(str(datetime.datetime.now()) + f"[ERROR] HTTP error exception occurred while querying: {err}")
# 	exit(1)
# except response.exceptions.TooManyRedirects:
# 	logger.error(str(datetime.datetime.now()) + f"[ERROR] Too many redirects with")
# 	exit(1)
# except response.exceptions.RequestException as err:
# 	logger.error(str(datetime.datetime.now()) + f"[ERROR] Requests had RequestException: {err}")
# 	exit(1)

# if response and response.status_code != 200:
# 	logger.error(f"Response returned a {response.status_code}")
# 	exit(1)
