import boto3
from botocore.exceptions import ClientError
import time
import redis

HOST = 'localhost'
PORT = '6379'
CHANNEL = 'motion-alert'

session = boto3.Session(profile_name='default')
# Any clients created from this session will use credentials
# from the [dev] section of ~/.aws/credentials.
ses_client = session.client('ses')

def send_email():
    try:
        response = ses_client.send_email(
            Source='xxx@gmail.com',
            Destination={
                'ToAddresses': [
                    'yyy@gmail.com',
                ]
            },
            Message={
                'Subject': {
                    'Data': 'Motion Detected'
                },
                'Body': {
                    'Text': {
                        'Data': 'Detect motion at ' + str(time.time())
                    }
                }
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

if __name__ == '__main__':
    r = redis.Redis(host=HOST, port=PORT)
    pub = r.pubsub()
    pub.subscribe(CHANNEL)

    while True:
        data = pub.get_message()
        if data:
            message = data['data']
            if message and message != 1:
                print("At {} - Message: {}".format(time.time(),message))
                print('Send warning email')
                send_email()

        time.sleep(0.05)