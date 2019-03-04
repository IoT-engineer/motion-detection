import boto3
from botocore.exceptions import ClientError
import time


session = boto3.Session(profile_name='default')
# Any clients created from this session will use credentials
# from the [dev] section of ~/.aws/credentials.
ses_client = session.client('ses')

try:
    response = ses_client.send_email(
        Source='yyy@gmail.com',
        Destination={
            'ToAddresses': [
                'xxx@gmail.com',
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