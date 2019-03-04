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
                    print('Send alert')
                    filter_pub = r.publish(
                        channel=FILTER_CHANNEL,
                        message='Send alert!'
                    )
                    LAST_PUB_MSG = NOW
        time.sleep(0.05)