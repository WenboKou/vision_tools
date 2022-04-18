import imageio
import os
import argparse

parser = argparse.ArgumentParser(description='get frames of the video') # container to hold arguments
parser.add_argument('--video_path', required=True, help='path of the video') # -- means optional, if not specified will be None
parser.add_argument('--frame_path', required=True, help='save path of the frames')
args = parser.parse_args()

def get_frames(video_path, frame_path):
    video_reader = imageio.get_reader(video_path)
    for idx, frame in enumerate(video_reader):
        print(f'processing the {idx}th')
        imageio.imsave(os.path.join(frame_path, f'{idx}.png'), frame)


if __name__ == '__main__':
    get_frames(args.video_path, args.frame_path)
