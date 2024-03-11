import logging
import time
import requests

yandex_token = ""
expires = 0
retrieve_time = time.time()

# сделать сихнронизацию
def retrieve_iam_token():
    global yandex_token
    global expires
    global retrieve_time
    if (retrieve_time + expires) < time.time():
        request = requests.get(
            url="http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token",
            headers={'Metadata-Flavor': 'Google'})
        json = request.json()
        yandex_token = json["access_token"]
        expires = json["expires_in"]
        retrieve_time = time.time()
        logging.info("Updating yandex token. New token: " + yandex_token
                     + ". Expires in " + time.strftime('%H:%M:%SZ', time.gmtime(expires)))
    return yandex_token
