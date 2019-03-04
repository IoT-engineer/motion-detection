# [AWS Learning]: Simple motion detection #


## What is this repository for? ##

This is an example explaining how to build a simple motion detector using raspberry and usb camera

![dirty-hand](./apps/single_cam_detector/pictures/architect.png?raw=true)

### Prerequites:

- Raspberry Pi 3 using Raspian Jessie
- A general USB camera
- Python programing
- AWS account with AWS SES enabled
  
### What will we build

- motion detector
- event publisher using redis broker
- event subscriber and sending alert email using AWS SES

### Application

- Home security
- Filtered source for object detection layer

## Steps Summary ##

- Setup motion project
- Setup redis
- Setup event publisher/emitter
- Setup event filter
- Setup email sender
- Connect your sender and event filter
- Start your security system

## How to set up ##

### Step1: Setup motion detector
- Install motion

Motion is an open-source project that monitors video signals from many types of cameras. Currently, it supports below devices:

    Network cameras via RTSP, RTMP and HTTP
    PI cameras
    V4L2 webcams
    Video capture cards
    Existing movie files

Beside, with motion we can wiew live stream of cameras as well as invoke scripts when activities occur.
This make motion be quite useful when we want to connect with other frameworks to create a full application.
You can get more details about it [here](https://motion-project.github.io/index.html).

Installation is also easy since motion already supported Raspberry Pi. Open a terminal and run these commands:

`sudo apt-get update && sudo apt-get upgrade`

`sudo apt-get install motion`

Now, verify if motion is working:

`sudo systemctl status motion`

You should see following ouput:

    * motion.service - LSB: Start Motion detection
       Loaded: loaded (/etc/init.d/motion)
       Active: active (exited) since Sun 2018-12-02 16:17:04 +07; 3 months 0 days ago
      Process: 511 ExecStart=/etc/init.d/motion start (code=exited, status=0/SUCCESS)

    Dec 02 16:17:04 raspberrypi systemd[1]: Started LSB: Start Motion detection.
    Dec 02 16:17:04 raspberrypi motion[511]: Not starting motion daemon, disabled via /etc/default/motion ... (warning).

- Configure motion

Before running, motion loads a file with .conf suffix, let's build our own config file by copying the default config. Take a look at sample config, you can change it if you want. Here are some important sections:

`videodevice /dev/video0`: your camera device.

`target_dir /path/to/your/working/directory`: directory where pictures capturing motion are stored

`picture_filename %v-%Y%m%d%H%M%S-%q`: Motion allows us to fomart the name of pictures stored when motion is detected.

You can find out definition of these format above `target_dir` section

    ############################################################
    # Target Directories and filenames For Images And Films
    # For the options snapshot_, picture_, movie_ and timelapse_filename
    # you can use conversion specifiers
    # %Y = year, %m = month, %d = date,
    # %H = hour, %M = minute, %S = second,
    # %v = event, %q = frame number, %t = thread (camera) number,
    # %D = changed pixels, %N = noise level,
    # %i and %J = width and height of motion area,
    # %K and %L = X and Y coordinates of motion center
    # %C = value defined by text_event
    # Quotation marks round string are allowed.
    ############################################################

Next, go to live stream server and check that it's enabled

    ############################################################
    # Live Stream Server
    ############################################################
    # The mini-http server listens to this port for requests (default: 0 = disabled)
    stream_port 8081
    ...
    # Restrict stream connections to localhost only (default: on)
    stream_localhost off

Here, we'll stream via LAN network on port 8081. We can use desktop or whatever browser on same network to view live stream. Finally, scroll down to `command` section

    ############################################################
    # External Commands, Warnings and Logging:
    # You can use conversion specifiers for the on_xxxx commands
    # %Y = year, %m = month, %d = date,
    # %H = hour, %M = minute, %S = second,
    # %v = event, %q = frame number, %t = thread (camera) number,
    # %D = changed pixels, %N = noise level,
    # %i and %J = width and height of motion area,
    # %K and %L = X and Y coordinates of motion center
    # %C = value defined by text_event
    # %f = filename with full path
    # %n = number indicating filetype
    # Both %f and %n are only defined for on_picture_save,
    # on_movie_start and on_movie_end
    # Quotation marks round string are allowed.
    ############################################################
    ...    
    # Command to be executed when a picture (.ppm|.jpg) is saved (default: none)
    # To give the filename as an argument to a command append it with %f
    on_picture_save /command/called/when/picture/saved
    ...


After `on_picture_save` is command called whenever a motion-capturing picture is save to your `target_dir`. We will write this command to publish an event that triggers filtering component of our system.

- Now, let's test motion

Firstly, run motion: `sudo motion -c /path/to/your/motion.conf`

Then, open your internet browser and type `<local-ip>:8081` press ENTER. You should see live video.

![dirty-hand](./apps/single_cam_detector/pictures/sample-01.png?raw=true)

### Step2: Setup redis

- Why redis
 
Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache and message broker. Here, we leverage `redis` as a pub/sub framework where motion detector triggers other parts of our system.

- How to install
  
`sudo apt-get install redis-server`

`sudo pip install redis`

Verify it

    sudo systemctl status redis-server
    * redis-server.service - Advanced key-value store
    Loaded: loaded (/lib/systemd/system/redis-server.service; enabled)
    Active: active (running) since Mon 2019-03-04 10:13:58 +07; 1min 49s ago
    Main PID: 30965 (redis-server)
    CGroup: /system.slice/redis-server.service
            `-30965 /usr/bin/redis-server 127.0.0.1:6379

    Mar 04 10:13:58 raspberrypi systemd[1]: Started Advanced key-value store.
    Mar 04 10:15:40 raspberrypi systemd[1]: Started Advanced key-value store.

- Testing using python script and command line

The idea is to write a simple python file to publish redis message then we'll receive it using command line. After that we'll call this script inside motion config file.
That's simple right ?. Open `publish_event.py` in folder `scripts`

    import redis
    import time

    HOST = 'localhost'
    PORT = '6379'
    CHANNEL = 'motion-detection-channel'

    if __name__ == '__main__':
        r = redis.Redis(host=HOST, port=PORT)
        pub = r.publish(
            channel=CHANNEL,
            message='Motion detected!'
        )

Open a terminal, subcribe to channel `motion-detection-channel`:

    pi@raspberrypi:~ $ redis-cli
    127.0.0.1:6379> SUBSCRIBE 'motion-detection-channel'
    Reading messages... (press Ctrl-C to quit)
    1) "subscribe"
    2) "motion-detection-channel"
    3) (integer) 1

At second one, run your python script

    pi@raspberrypi:~/path/to/python/file $ python publish_event.py

Back to first terminal, you should see

    1) "message"
    2) "motion-detection-channel"
    3) "Motion detected!"

Congratulations! Your pub/sub is working !

### Step3: Setup event publisher/emitter


- Time to write your publisher.

Put this script to you `motion.conf` file. Please change the path
`on_picture_save python /path/to/your/scripts/publish_event.py` to fit your case.

- Testing

Run motion again and make some movements before camera, you should see a lot of messages will be published.

    1) "message"
    2) "motion-detection-channel"
    3) "Motion detected!"
    1) "message"
    2) "motion-detection-channel"
    3) "Motion detected!"
    ...

It worked but looks like a spam. That's why we need filter event on next step.

### Step4: Setup event filter

As you can see, one simple movement could produce a lot of triggers, so we want to filter them using interval time. For example, only continue processing received messages every 5 seconds. This help us avoid causing a spam to user via email. That also helps decrease AWS cost.

Check file `filter_event.py`, this subcribes to "motion-detection-channel" and publishes a new message to topic "motion-alert" using time-slice filter.

    import redis
    import time

    HOST = 'localhost'
    PORT = '6379'
    CHANNEL = 'motion-detection-channel'
    FILTER_CHANNEL = 'motion-alert'
    LAST_PUB_MSG = time.time()
    INTERVAL_TIME = 5.0 #5 seconds

    if __name__ == '__main__':
        r = redis.Redis(host=HOST, port=PORT)
        pub = r.pubsub()
        pub.subscribe(CHANNEL)

        while True:
            data = pub.get_message()
            if data:
                message = data['data']
                if message and message != 1:
                    print("Received message: {}".format(message))
                    NOW = time.time()
                    DELTA = NOW-LAST_PUB_MSG
                    if DELTA > INTERVAL_TIME:
                        filter_pub = r.publish(
                            channel=FILTER_CHANNEL,
                            message='Send alert!'
                        )
                        LAST_PUB_MSG = NOW
            time.sleep(0.05)

Run this script, you should see filter output:

    python subscribe_filtered_event.py 
    At 1551672910.2109606 - Message: b'Send alert!'
    At 1551672916.2169352 - Message: b'Send alert!'
    At 1551672922.2231312 - Message: b'Send alert!'
    At 1551672927.227488 - Message: b'Send alert!'
    At 1551672932.232431 - Message: b'Send alert!'

You can change `INTERVAL_TIME` to higher or lower depend on your requirements.

### Step5: Setup email sender

On this part, we will use AWS SES to send email to users based on messages coming from filtered channel

#### Install boto3 library and aws cli

`sudo pip install boto3`

`sudo pip install awscli`

#### Configure your aws account:
Input  `your-access-key`, `your-secret-key` as well as  `your-region`

    pi@raspberrypi:~ $ aws configure
    AWS Access Key ID [None]: <your-access-key>
    AWS Secret Access Key [None]: <your-secret-key>
    Default region name [None]: <your-region>
    Default output format [None]:

Then press enter. You can check these values by typing:

`cat ~/.aws/config` and `cat ~/.aws/credentials`

#### Configure AWS SES

You have to register your email. Here is one example. If you want register another ones, goto `SES condole` and click `Verify a New Email Address`

![ses-console](./apps/single_cam_detector/pictures/ses-console.png?raw=true)

AWS SES would send a verification email contains active link like this

![verify-email](./apps/single_cam_detector/pictures/verify-email.png?raw=true)

#### Now test your sender

Modify script `send_email.py` by replacing **your-email** , **receiver-email**

    import boto3
    from botocore.exceptions import ClientError
    import time


    session = boto3.Session(profile_name='default')
    # Any clients created from this session will use credentials
    # from the [dev] section of ~/.aws/credentials.
    ses_client = session.client('ses')

    try:
        response = ses_client.send_email(
            Source='<your-email>',
            Destination={
                'ToAddresses': [
                    '<receiver-email>',
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

Run this file

    python send_email.py 
    Email sent! Message ID: <a-lot-of-number>

and check inbox, you should see similar email

![sample-email](./apps/single_cam_detector/pictures/sample-email.png?raw=true)

Voilà! Your sender worked !

### Step6: Connect your sender and event filter

Modify send_email.py to listen on FILTER_CHANNEL, it's easy for you now, right ? You can see full detail at my repo. Here I only show some lines of code:

    def send_email():
        try:
            response = ses_client.send_email(
                Source='<your-email>',
                Destination={
                    'ToAddresses': [
                        '<receiver-email>',
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

Here, we wrap code sending email into a function name `send_email`. Put it in `main` function.

### Step7: Start your security system

Open 3 terminal and run

Start motion: `sudo motion -c /path/to/your/motion.conf` 

Start filter: `python filter_event.py `

Start sender: `python send_email.py`

Goto your browwser and enter this URL `<local-ip>:8081` to watch live stream video

Make some motion and Check your email

![final-result](./apps/single_cam_detector/pictures/final-result.png?raw=true)

## Conclusion

Via some simple steps, we can setup an motion detector using 35$ computer.
There are many points to improve here, such as:
- move filtering code into sender
- make detector auto start at boottime
- detect human and animal in images,..

I hope to implement these features on next posts. 
Finally. thank you for reading.

## What's next? ##

- Try double cameras
- Power your detector using AWS IoT