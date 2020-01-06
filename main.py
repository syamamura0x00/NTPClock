#!/usr/bin/env python

import sys
import time
import logging

import pygame
from pygame.locals import *

# from PySide2 import QtCore, QtGui, QtWidgets


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

IS_FULLSCREEN = False
FRAME_RATE = 60
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

COLOR_BG = 0x394552
COLOR_FONT = 0xE1EBF5
COLOR_BOLD = 0xF7665C
COLOR_INFO = 0xB4C43B


def main():
    logging.basicConfig(level=logging.DEBUG)

    ntp_client = NTPClient(NTP_SERVER_LIST, TIMEZONE)
    ntp_client.sync()

    pygame.init()

    # Initialize screen
    display_info = pygame.display.Info()
    screen_bitsize = display_info.bitsize
    scrreen_width = display_info.current_w
    scrreen_height = display_info.current_h

    display_driver = pygame.display.get_driver()

    logging.info(f"Pygame: display_driver={display_driver}")
    # print(display_info)

    screen_flags = pygame.DOUBLEBUF
    if IS_FULLSCREEN:
        screen_flags |= pygame.FULLSCREEN | pygame.HWSURFACE
    else:
        screen_flags |= pygame.RESIZABLE

    screen = pygame.display.set_mode((scrreen_width, scrreen_height), screen_flags, screen_bitsize)
    screen_2 = pygame.display.set_mode((scrreen_width, scrreen_height), screen_flags, screen_bitsize)
    pygame.display.set_caption("NTPClock")

    clock = pygame.time.Clock()

    # Initialize fonts
    main_clock_font = pygame.font.SysFont(None, 120)

    accumulation_fps = []
    avg_fps = 0.0
    one_sec_timer = time.time()

    while True:
        frame_start_time = time.time()

        current_dt = ntp_client.get_datetime()
        current_str = current_dt.strftime("%Y/%m/%d %H:%M:%S") + f".{str(current_dt.microsecond)[0:1]}"
        # sys.stdout.write(f"{current_str}\r")

        main_clock_rander = main_clock_font.render(current_str, False, get_rgb(COLOR_FONT))

        for event in pygame.event.get(): # 終了処理
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # ================================================================
        # Draw
        # ================================================================
        screen.fill(get_rgb(COLOR_BG))

        screen.blit(main_clock_rander, (50, 20))

        pygame.display.flip()
        # pygame.display.update()

        frame_time = time.time() - frame_start_time
        vsync_wait = 1.0 / FRAME_RATE

        if vsync_wait > frame_time:
            time.sleep(vsync_wait - frame_time)

        frame_time = time.time() - frame_start_time
        fps = 1.0 / (frame_time)
        accumulation_fps.append(fps)

        if time.time() - one_sec_timer > 1.0:
            one_sec_timer = time.time()
            if len(accumulation_fps):
                avg_fps = sum(accumulation_fps) / len(accumulation_fps)

        pygame.display.set_caption(f"NTPClock [FPS: {fps:.02f}, Avg.: {avg_fps:.02f}]")






def get_rgb(hex):
    r = hex >> 16 & 0xFF
    g = hex >> 8 & 0xFF
    b = hex >> 0 & 0xFF
    return (r, g, b)




if __name__ == "__main__":
    main()
