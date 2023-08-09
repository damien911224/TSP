import os
import glob

from ctypes import c_int
from multiprocessing import Pool, Value, Lock, current_process

def standardize(video_file_path):
    # Global variables to indicate the progress
    global progress_counter, progress_counter_lock, global_dst_folder

    # Get the video file name and video identity
    video_name = video_file_path.split('/')[-1]
    video_id = video_name.split('.')[-2]

    # out_full_path: video folder
    # image_full_path: folder of RGB frames
    out_full_path = os.path.join(global_dst_folder, video_id + ".mp4")

    cmd = "ffmpeg -loglevel panic -y -i {} -filter:v fps=fps=30 {}".format(video_file_path, out_full_path)

    # Now, extract the frames.
    with progress_counter_lock:
        progress_counter.value += 1
        print('Standardize Videos ... {:05d} {:06.2f}%'.format(
            progress_counter.value,
            float(progress_counter.value) / float(len(self.video_files)) * 100.0
        ))

    # Enter the command to the system and flush
    os.system(cmd)
    sys.stdout.flush()

if __name__ == '__main__':

    video_files = glob.glob(os.path.join('/mnt/hdd0/kinetics-dataset/k400/train', '*'))
    video_files += glob.glob(os.path.join('/mnt/hdd0/kinetics-dataset/k400/val', '*'))
    video_files += glob.glob(os.path.join('/mnt/hdd0/kinetics-dataset/k400/test', '*'))
    dst_folder = os.path.join('/mnt/hdd0/kinetics-dataset/k400/standardized_videos')

    num_workers = 20

    # Global variables to indicate the progress
    global progress_counter, progress_counter_lock, global_dst_folder
    progress_counter = Value(c_int)
    progress_counter_lock = Lock()
    global_dst_folder = dst_folder

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