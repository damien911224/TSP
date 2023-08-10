import os
import sys
import glob
import cv2

from shutil import copy
from ctypes import c_int
from multiprocessing import Pool, Value, Lock, current_process

def standardize(video_file_path):
    # Global variables to indicate the progress
    global progress_counter, progress_counter_lock, global_dst_folder, global_len

    # Get the video file name and video identity
    video_name = video_file_path.split('/')[-1]
    video_id = video_name.split('.')[-2]
    out_full_path = os.path.join(global_dst_folder, video_id + ".mp4")

    if os.path.exists(out_full_path):
        try:
            video_cap = cv2.VideoCapture(out_full_path)
            if video_cap.isOpened():
                video_cap.release()
                with progress_counter_lock:
                    progress_counter.value += 1
                    print('Standardize Videos ... {:05d} {:06.2f}% PASS :)'.format(
                        progress_counter.value,
                        float(progress_counter.value) / float(global_len) * 100.0
                    ))
                return
        except:
            pass

    try:
        video_cap = cv2.VideoCapture(video_file_path)
    except:
        with progress_counter_lock:
            progress_counter.value += 1
            print('Standardize Videos ... {:05d} {:06.2f}% ERROR: VIDEO CAP :('.format(
                progress_counter.value,
                float(progress_counter.value) / float(global_len) * 100.0
            ))
        return

    if not video_cap.isOpened():
        video_cap.release()
        with progress_counter_lock:
            progress_counter.value += 1
            print('Standardize Videos ... {:05d} {:06.2f}% ERROR: VIDEO CAP :('.format(
                progress_counter.value,
                float(progress_counter.value) / float(global_len) * 100.0
            ))
        return
    else:
        try:
            fps = video_cap.get(cv2.CAP_PROP_FPS)
            ext = video_name.split(".")[-1]
            if fps == 30.0 and ext == "mp4":
                copy(video_file_path, out_full_path)
                video_cap.release()
                with progress_counter_lock:
                    progress_counter.value += 1
                    print('Standardize Videos ... {:05d} {:06.2f}% COPY :)'.format(
                        progress_counter.value,
                        float(progress_counter.value) / float(global_len) * 100.0
                    ))
                return
        except:
            pass
    video_cap.release()

    cmd = "ffmpeg -loglevel panic -y -i {} -filter:v fps=fps=30 {}".format(video_file_path, out_full_path)

    # Now, extract the frames.
    with progress_counter_lock:
        progress_counter.value += 1
        print('Standardize Videos ... {:05d} {:06.2f}%'.format(
            progress_counter.value,
            float(progress_counter.value) / float(global_len) * 100.0
        ))

    # Enter the command to the system and flush
    os.system(cmd)
    sys.stdout.flush()

if __name__ == '__main__':

    video_files = glob.glob(os.path.join('/mnt/hdd0/kinetics/train', '*'))
    video_files += glob.glob(os.path.join('/mnt/hdd0/kinetics/val', '*'))
    video_files += glob.glob(os.path.join('/mnt/hdd0/kinetics/test', '*'))
    video_files += glob.glob(os.path.join('/mnt/hdd0/kinetics/replacement', '*'))
    dst_folder = os.path.join('/mnt/hdd0/kinetics/standardized_videos')

    num_workers = 56

    # Global variables to indicate the progress
    global progress_counter, progress_counter_lock, global_dst_folder, global_len
    progress_counter = Value(c_int)
    progress_counter_lock = Lock()
    global_dst_folder = dst_folder
    global_len = len(video_files)

    # Make the destination folder
    if not os.path.exists(dst_folder):
        try:
            os.mkdir(dst_folder)
        except OSError:
            pass

    # Multiprocessing
    pool = Pool(processes=num_workers)
    pool.map(standardize, video_files)
    pool.close()
    pool.join()