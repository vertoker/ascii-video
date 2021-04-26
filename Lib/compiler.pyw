import cv2, time, sys, os, pickle
import tkinter.filedialog, pygame
from multiprocessing import Process
import moviepy.editor as mp
from PIL import Image
import tkinter as tk

base = tk.Tk()
base.title("Compiler video to ASCII (mp4 to mpascii)")
text_box = tk.Text(bg = "black", fg = "white")
text_box.pack()

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", " "]
frame_size = 150
aspect_ratio = 16 / 9
frame_interval = 1.0 / 30.75
ASCII_LIST = []

lines = ['']
def console(text, erase_line = True, next_line = True):
    if erase_line:
        text += '\n'
    lines[-1] = text
    if next_line:
        lines.append('')

    text = ''
    for line in lines:
        text += line

    text_box.delete("1.0", tk.END)
    text_box.insert("1.0", text)
    base.update()

# Extract frames from video
def extract_transform_generate(video_path, start_frame, number_of_frames = 1000):
    capture = cv2.VideoCapture(video_path)
    capture.set(1, start_frame)  # Points cap to target frame
    current_frame = start_frame
    frame_count = 1

    ret, image_frame = capture.read()
    height, width, layers = image_frame.shape
    aspect_ratio = (height / float(width * 2.5))

    while ret and frame_count <= number_of_frames:
        ret, image_frame = capture.read()
        try:
            image = Image.fromarray(image_frame)
            ascii_characters = pixels_to_ascii(greyscale(resize_image(image)))  # get ascii characters
            pixel_count = len(ascii_characters)
            ascii_image = "\n".join([ascii_characters[index:(index + frame_size)] for index in range(0, pixel_count, frame_size)])
            ASCII_LIST.append(ascii_image)
        except Exception as error:
            continue

        progress_bar(frame_count, number_of_frames)
        frame_count += 1  # increases internal frame counter
        current_frame += 1  # increases global frame counter

    capture.release()

# Progress bar code is courtesy of StackOverflow user: Aravind Voggu.
# Link to thread: https://stackoverflow.com/questions/6169217/replace-console-output-in-python
def progress_bar(current, total, barLength=25):
    progress = float(current) * 100 / total
    arrow = '#' * int(progress / 100 * barLength - 1)
    spaces = ' ' * (barLength - len(arrow))
    console('\rProgress: [%s%s] %d%% Frame %d of %d frames' % (arrow, spaces, progress, current, total), True, False)

# Resize image
def resize_image(image_frame):
    width, height = image_frame.size
    aspect_ratio = (height / float(width * 2.5))  # 2.5 modifier to offset vertical scaling on console
    new_height = int(aspect_ratio * frame_size)
    resized_image = image_frame.resize((frame_size, new_height))
    # print('Aspect ratio: %f' % aspect_ratio)
    # print('New dimensions %d %d' % resized_image.size)
    return resized_image

# Greyscale
def greyscale(image_frame):
    return image_frame.convert("L")

# Convert pixels to ascii
def pixels_to_ascii(image_frame):
    pixels = image_frame.getdata()
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters

# Open image => Resize => Greyscale => Convert to ASCII => Store in text file
def ascii_generator(image_path, start_frame, number_of_frames):
    current_frame = start_frame
    while current_frame <= number_of_frames:
        path_to_image = image_path + '/BadApple_' + str(current_frame) + '.jpg'
        image = Image.open(path_to_image)
        ascii_characters = pixels_to_ascii(greyscale(resize_image(image)))  # get ascii characters
        pixel_count = len(ascii_characters)
        ascii_image = "\n".join([ascii_characters[index:(index + frame_size)] for index in range(0, pixel_count, frame_size)])
        file_name = r"TextFiles/" + "bad_apple" + str(current_frame) + ".txt"
        try:
            with open(file_name, "w") as f:
                f.write(ascii_image)
        except FileNotFoundError:
            continue
        current_frame += 1

def preflight_operations(path):
    if os.path.exists(path):
        path_to_video = path.strip()
        cap = cv2.VideoCapture(path_to_video)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        video = mp.VideoFileClip(path_to_video)
        audio = video.audio.to_soundarray(nbytes = 4, quantize = True)

        frames_per_process = int(total_frames / 4)
        process1_end_frame = frames_per_process
        process2_start_frame = process1_end_frame + 1
        process2_end_frame = process2_start_frame + frames_per_process
        process3_start_frame = process2_end_frame + 1
        process3_end_frame = process3_start_frame + frames_per_process
        process4_start_frame = process3_end_frame + 1
        process4_end_frame = total_frames - 1

        start_time = time.time()
        console('Beginning ASCII generation...')
        extract_transform_generate(path_to_video, 1, process4_end_frame)
        execution_time = time.time() - start_time
        console('ASCII generation completed! ASCII generation time: ' + str(execution_time) + ' seconds')

        return [[total_frames, frame_size, int(frame_size / aspect_ratio)], ASCII_LIST, audio]

    else:
        console('Warning file not found!')

def input_open_file_name():
    user_input = tk.filedialog.askopenfilename(filetypes = (("Video files", "*.mp4*"), ("All files", "*.*")))
    if user_input == '':
        return input_open_file_name()
    return user_input

def file_save(data):
    # mpascii - Moving Pictures American Standard Code for Information Interchange
    name = tk.filedialog.asksaveasfile(mode = 'w', defaultextension = ".mpascii")
    with open(name.name, "wb") as fp:
        pickle.dump(data, fp)

def main():
    console("Choose folder the video file name: ", False)
    user_input = input_open_file_name()
    console(user_input)
    data = preflight_operations(user_input)
    file_save(data)

if __name__ == '__main__':
    main()
