import cv2, time, sys, os, pickle
import pygame, fpstimer, argparse
import pathlib, threading
from multiprocessing import Process
import moviepy.editor as mp
from PIL import Image

import tkinter as tk
from tkinter import ttk
from functools import partial
from tkinter.font import Font
from tkinter.filedialog import askopenfilename

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
current_frame = 0
is_playing = True

def timer_thread():
    global current_frame
    timer = fpstimer.FPSTimer(30)
    while (is_playing):
        current_frame += 1
        timer.sleep()

def load_file(path):
    with open(path, "rb") as fp:
        data = pickle.load(fp)
    data[2] = data[2].astype('int16')
    return data

def delete_window():
    os._exit(1)
    exit()

def main(path):#903 586
    global is_playing, current_frame
    font_size = 8

    data = load_file(path)
    frames_counter = data[0][0]
    width = data[0][1]
    height = data[0][2]
    screen_width = int(data[0][1] * font_size)
    screen_height = int(data[0][2] * font_size)

    base = tk.Tk()
    base.title("MPASCII Player")
    base.protocol("WM_DELETE_WINDOW", delete_window)
    base.geometry(str(screen_width) + "x" + str(screen_height))
    base.configure(background = 'black')
    theme = ttk.Style()
    theme.theme_use("alt")

    text_box = tk.Text(width = screen_width, height = screen_height, bg = "black", fg = "white", font = ("Consolas", font_size))
    text_box.pack()

    # audio and video init
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    sound = pygame.sndarray.make_sound(data[2])

    def main_thread():
        timer = fpstimer.FPSTimer(30)
        while (is_playing):
            text_box.delete("1.0", tk.END)
            text_box.insert("1.0", data[1][current_frame])
            base.update()
            timer.sleep()
    def pause():
        if is_playing:
            is_playing = False
            video.stop()
        else:
            is_playing = True
            video.start()

    control_panel = ttk.Frame(base)
    pause_but = ttk.Button(control_panel, text="Pause", command=pause)
    pause_but.pack(side = tk.LEFT)
    control_panel.pack(side = tk.BOTTOM)
    timer = threading.Thread(target = timer_thread)
    # start
    sound.play()
    timer.start()
    main_thread()

#"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Create a ArcHydro schema')
    parser.add_argument('--path', metavar = 'path', required = True, help = 'the path of video')
    args = parser.parse_args()
    main(path = args.path)
#"""
#main('B:\\PythonProjects\\ascii-video\\BadApple.mpascii')
