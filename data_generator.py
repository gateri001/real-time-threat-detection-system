import time, random, json
import numpy as np
import pandas as pd
from datetime import datetime

SRC_IPS = [f"10.0.0.{i}" for i in range(2,120)]
DST_IPS = [f"172.16.0.{i}" for i in range(2,60)]
PROTOCOLS = ["TCP","UDP","ICMP"]

def random_event(attack=False):
    src = random.choice(SRC_IPS) if not attack else random.choice(SRC_IPS[:5])
    dst = random.choice(DST_IPS)
    bytes_sent = int(np.random.exponential(300))
    pkts = max(1, int(bytes_sent/200))
    proto = random.choice(PROTOCOLS)
    flags = random.choice(["SYN","ACK","PSH",""])
    timestamp = datetime.utcnow().isoformat()
    # attack scenario: high bytes, many pkts, repeated ports
    if attack and random.random() < 0.8:
        bytes_sent *= 50
        pkts *= 40
        proto = "TCP"
        flags = "SYN"
    return {
        "timestamp": timestamp,
        "src_ip": src,
        "dst_ip": dst,
        "bytes": bytes_sent,
        "pkts": pkts,
        "proto": proto,
        "flags": flags
    }

def stream_events(callback, interval=0.2):
    while True:
        # occasional attack burst
        attack = random.random() < 0.05
        event = random_event(attack=attack)
        callback(event)
        time.sleep(interval)

if __name__ == "__main__":
    # prints to stdout
    def cb(e): print(json.dumps(e))
    stream_events(cb)
