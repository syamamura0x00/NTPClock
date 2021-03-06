#!/usr/bin/env python

import os
import sys
import time
import logging

import pygame
from pygame.locals import *

# from PySide2 import QtCore, QtGui, QtWidgets


from ntp import NTPClient
import process_mon


NTP_SERVER_LIST = [
    "ntp.nict.jp"
    # , "ntp.jst.mfeed.ad.jp"
    # , "time.cloudflare.com"
    , "time.google.com"
    # , "ats1.e-timing.ne.jp"
    # , "s2csntp.miz.nao.ac.jp"
]

TIMEZONE = +9

IS_FULLSCREEN = True
FRAME_RATE = 20
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

COLOR_BG = 0x394552
COLOR_FONT = 0xE1EBF5
COLOR_BOLD = 0xF7665C
COLOR_INFO = 0xB4C43B


def main():
    logging.basicConfig(level=logging.DEBUG)

    process_monitor = process_mon.ProcessMonitor()

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
    main_date_font = pygame.font.SysFont(None, 190)
    main_clock_font = pygame.font.SysFont(None, 320)
    main_sec_font = pygame.font.SysFont(None, 240)
    fps_font = pygame.font.SysFont(None, 64)

    accumulation_fps = []
    avg_fps = 0.0
    fps = 0.0
    one_sec_timer = time.time()
    last_sync_time = time.time()

    process_monitor.start()

    while True:
        if time.time() - last_sync_time > 3600.0:
            ntp_client.sync()

        # 時刻レンダリング
        frame_start_time = time.time()

        current_dt = ntp_client.get_datetime()

        current_date_str = current_dt.strftime("%Y/%m/%d(%a)")
        current_clock_str = current_dt.strftime("%H:%M")
        current_sec_str = f"{current_dt.second:02d}.{str(current_dt.microsecond)[0:1]}"

        main_date_render = main_date_font.render(current_date_str, False, get_rgb(COLOR_FONT))
        main_clock_render = main_clock_font.render(current_clock_str, False, get_rgb(COLOR_FONT))
        main_sec_render = main_sec_font.render(current_sec_str, False, get_rgb(COLOR_FONT))

        main_date_size_w, main_date_size_h = main_date_font.size(current_date_str)
        main_clock_size_w, main_clock_size_h = main_clock_font.size(current_clock_str)
        main_sec_size_w, main_sec_size_h = main_sec_font.size(current_sec_str)


        # FPSレンダリング
        fps_render = fps_font.render(f"{avg_fps:.02f} FPS", False, get_rgb(0x00FF00))

        # ================================================================
        # イベント処理
        # ================================================================
        for event in pygame.event.get(): # 終了処理
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    pygame.quit()
                    os._exit(0)

        # ================================================================
        # Draw
        # ================================================================
        screen.fill(get_rgb(COLOR_BG))

        screen.blit(main_date_render, (int(scrreen_height  - (main_date_size_w / 2)), 80))
        screen.blit(main_clock_render, (int(scrreen_height  - (main_clock_size_w / 2) - (main_sec_size_w / 2) - 16), scrreen_height / 2 - 60))
        screen.blit(main_sec_render, (int(scrreen_height  - (main_sec_size_w / 2) + (main_clock_size_w / 2) + 16), (scrreen_height / 2 - 60) + main_clock_size_h - main_sec_size_h))

        screen.blit(fps_render, (5, 5))

        pygame.display.flip()


        # ================================================================
        # FPS計測
        # ================================================================
        frame_time = time.time() - frame_start_time

        fps = 1.0 / (frame_time)
        accumulation_fps.append(fps)

        if time.time() - one_sec_timer > 1.0:
            one_sec_timer = time.time()
            if len(accumulation_fps):
                avg_fps = sum(accumulation_fps) / len(accumulation_fps)

        # pygame.display.set_caption(f"NTPClock [FPS: {fps:.02f}, Avg.: {avg_fps:.02f}]")

        # ================================================================
        # VSYNC
        # ================================================================
        vsync_wait = 1.0 / FRAME_RATE

        if vsync_wait > frame_time:
            time.sleep(vsync_wait - frame_time)

        time.sleep(0.05)

        process_monitor.process_message()


def get_rgb(hex):
    r = hex >> 16 & 0xFF
    g = hex >> 8 & 0xFF
    b = hex >> 0 & 0xFF
    return (r, g, b)




if __name__ == "__main__":
    main()
