#!/usr/bin/env python

import sys

from ntp import NTPClient


NTP_SERVER_LIST = [
    "ntp.nict.jp"
    , "ntp.jst.mfeed.ad.jp"
    , "time.cloudflare.com"
    , "time.google.com"
    , "ats1.e-timing.ne.jp"
    , "s2csntp.miz.nao.ac.jp"
]

TIMEZONE = +9

def main():
    ntp_client = NTPClient(NTP_SERVER_LIST, TIMEZONE)
    ntp_client.sync()

    while True:
        current_dt = ntp_client.get_datetime()

        sys.stdout.write(current_dt.strftime("%Y-%m-%d %H:%M:%S") + f".{current_dt.microsecond}")
        sys.stdout.write("\r")


if __name__ == "__main__":
    main()
