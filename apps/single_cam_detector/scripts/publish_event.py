#!/bin/bash
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
