#!/usr/bin/env python

import sys
import time
import datetime

import ntplib

from kivy.app import App
from kivy.uix.label import Label
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ListProperty


Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')

"""
certifi==2019.11.28
chardet==3.0.4
docutils==0.15.2
idna==2.8
Kivy==1.11.1
Kivy-Garden==0.1.4
ntplib==0.3.3
Pygments==2.5.2
requests==2.22.0
urllib3==1.25.7
"""

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
    ts_list = []
    base_time = time.time()

    for host in NTP_SERVER_LIST:
        try:
            remote_time = get_time(host)
        except ntplib.NTPException as e:
            continue

        ts_list.append(
            {
                "host": host
                , "correction": time.time() - base_time
                , "remote_time": remote_time
                , "correctioned_remote_time": None
            }
        )

        # time.sleep(1)

    correction_time = time.time() - base_time

    times = []
    for ts in ts_list:
        ts["correctioned_remote_time"] = (ts["remote_time"] - ts["correction"]) + correction_time
        times.append(ts["correctioned_remote_time"])
        print("{:<24}remote: {:.08f}\tcorrectioned_remote: {:.08f}".format(ts["host"], ts["remote_time"], ts["correctioned_remote_time"]))

        time.sleep(0.2)


    avg_time = sum(times) / len(times)

    print(avg_time)

    while True:
        current_ts = avg_time + (correction_time + time.time() - base_time)

        current_dt = datetime.datetime.fromtimestamp(current_ts, datetime.timezone(datetime.timedelta(hours=TIMEZONE)))

        sys.stdout.write(current_dt.strftime("%Y-%m-%d %H:%M:%S") + f".{current_dt.microsecond}")
        sys.stdout.write("\r")

        time.sleep(0.016)




def get_time(host):
    ntp_client = ntplib.NTPClient()
    res = ntp_client.request(host)

    return res.tx_time


class MainTimeWidget(Widget):
    text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self, str_time):
        self.text = str_time

    def build(self):
        return Label(size_hint_y=1.8, font_size=30, text=self.text)


class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_time_widget = None

    def build(self):
        self.main_time_widget = MainTimeWidget()
        return self.main_time_widget




if __name__ == "__main__":
    MainApp().run()
    main()
