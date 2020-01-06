
import time
import datetime
import logging

import ntplib


class NTPClient(object):
    def __init__(self, ntp_server_list, timezone=0):
        self._ntp_server_list = ntp_server_list
        self._clients = [_Time(host) for host in self._ntp_server_list]
        self._base_time = None
        self._timezone = timezone
        self.avg_time = None


    def sync(self):
        self._base_time = time.time()

        for client in self._clients:
            client.update(self._base_time)

        self._correction_time = time.time() - self._base_time

    def get_datetime(self):

        times = []

        for client in self._clients:
            if not client.is_failed:
                ts = client.correctioned_remote_time + self._correction_time
                times.append(ts)
                # print(f"{client.host:<24}{ts:.08f}")

        avg_time = sum(times) / len(times)

        current_ts = avg_time + (self._correction_time + time.time() - self._base_time)
        current_dt = datetime.datetime.fromtimestamp(current_ts, datetime.timezone(datetime.timedelta(hours=self._timezone)))

        # sys.stdout.write(current_dt.strftime("%Y-%m-%d %H:%M:%S") + f".{current_dt.microsecond}")
        # sys.stdout.write("\r")

        # time.sleep(0.016)

        return current_dt


class _Time(object):
    def __init__(self, host):
        self.is_failed = False
        self.host = host
        self.correctioned_remote_time = None

    def update(self, base_time):
        try:
            remote_time = self.get_time(self.host)
            correction_time = time.time() - base_time
            self.is_failed = False
            logging.info(f"Sync time: host={self.host}, remote_time={remote_time}")

        except ntplib.NTPException as e:
            self.is_failed = True
            logging.error(f"Sync time failed: host={self.host}, message={e}")
            return

        self.correctioned_remote_time = remote_time - correction_time


    def get_time(self, host):
        ntp_client = ntplib.NTPClient()
        res = ntp_client.request(host)

        return res.tx_time
