import os
import time
import json
import datetime
from moviepy.editor import VideoFileClip


class VideoControl:
    def __init__(self, root=None, video_in_list=None):
        video_root_dir = list()
        if root is None:
            self.root = '../video/'
        else:
            self.root = root

        root_name = ['in_files', 'out_files']
        for dir_name in root_name:
            video_root_dir.append(os.path.join(self.root, dir_name))
            if not os.path.exists(video_root_dir[-1]):
                os.makedirs(video_root_dir[-1])
        self.video_root = video_root_dir

        self.video_in_path = list()
        if video_in_list is None:
            self.video_in_list = ['misaeng.S1.E0001.mp4']
        else:
            self.video_in_list = video_in_list

        for video_name in self.video_in_list:
            self.video_in_path.append(os.path.join(self.video_root[0], video_name))

        print(self.video_in_path)

    def get_video_out_path(self, start_end, use_GPU, codec):
        video_out_list = list()
        is_full = 'full' if start_end is None else get_time_info(start_end)
        if not use_GPU:
            CPU_GPU = 'CPU'
        else:
            CPU_GPU = 'GPU'

        for name in self.video_in_list:
            name, ext = os.path.splitext(name)
            video_out_list.append('{}_{}_{}_{}.mp4'.format(name, is_full, CPU_GPU, codec))

        video_out_path = list()
        temp_audio_path = list()
        for video_out_name in video_out_list:
            video_out_path.append(os.path.join(self.video_root[1], video_out_name))
            temp_audio_path.append(os.path.join(self.video_root[1], os.path.splitext(video_out_name)[0] + '.mp3'))

        print(video_out_path)

        return video_out_path, temp_audio_path, CPU_GPU

    def encoding_videos(self, start_end=None, use_GPU=False, codec='libx264'):
        video_out_path, temp_audio_path, CPU_GPU = self.get_video_out_path(start_end, use_GPU, codec)
        duration = dict()
        for i, in_path in enumerate(self.video_in_path):
            out_path = video_out_path[i]

            start_time = time.time()
            clip = VideoFileClip(in_path)
            if start_end is not None:
                clip = clip.subclip(*start_end)
            clip.write_videofile(out_path,
                                 write_logfile=True, codec=codec, temp_audiofile=temp_audio_path[i])
            clip.close()
            duration[out_path] = dict()
            duration[out_path]['time'] = str(datetime.timedelta(seconds=(time.time() - start_time)))
            duration[out_path]['device'] = CPU_GPU
            duration[out_path]['codec'] = codec
            duration[out_path]['start_end'] = start_end
            print(duration[out_path]['time'])
        print(duration)
        curr_time = datetime.datetime.now()
        curr_time_str = '{}-{}-{}_{}.{}.{}'.format(curr_time.year, curr_time.month, curr_time.day,
                                                   curr_time.hour, curr_time.minute, curr_time.second)
        json_path = os.path.join(self.root, '{}_log.json'.format(curr_time_str))
        json.dump(duration, open(json_path, 'w'), indent=2)


def get_time_info(start_end):
    time_str = list()
    for time_data in start_end:
        if isinstance(time_data, int):
            time_str.append('0.0.{}'.format(str(time_data)))
        elif isinstance(time_data, tuple):
            if len(time_data) == 2:
                minute, second = time_data
                time_str.append('0.{}.{}'.format(str(minute), str(second)))
            else:
                hour, minute, second = time_data
                time_str.append('{}.{}.{}'.format(str(hour), str(minute), str(second)))
        else:
            time_str.append(time_data)

    output_str = '{}-{}'.format(*time_str)

    return output_str


# 00:00:00.000 -> frame_num 바꿔주는 함수
def get_sound_frame(sound_time):
    parse_hour, parse_min, parse_sec = sound_time.split(':')
    total_time = float(parse_hour) * 3600 + float(parse_min) * 60 + float(parse_sec)
    frame_num = round(total_time * 29.96, 2)

    return str(frame_num)


def get_frame_to_time(frame, fps):
    """
    frame, fps를 입력받아 second와 str(time)을 return하는 함수
    :param frame: int
    :param fps: int
    :return: (second: float, time: str)
        second : ##.###
        time : "hh:mm:ss.mmm"
    """
    second = round(float(frame) / fps, 3)
    left = second
    str_time = str()
    hms = [3600, 60, 1]
    for under in hms:
        if under != 1:
            elem = int(left / under)
            prefix_for_check = str(elem)
            prefix = '0' * (2 - len(prefix_for_check))
            suffix = str(elem)
        else:
            elem = round(left, 3)
            prefix_for_check, suffix_for_check = str(elem).split('.')
            prefix = '0' * (2 - len(prefix_for_check))
            suffix = str(elem) + '0' * (3 - len(suffix_for_check))
        str_time += prefix + suffix
        if under != 1:
            str_time += ':'
        left -= elem * under

    return second, str_time


if __name__ == '__main__':
    video_in = ['misaeng.S1.E0001.mp4', 'BG_2402.mpg']
    use_GPU = [False]
    # use_GPU = True
    start_end = [None]
    # start_end = None
    codecs = ['libx264']
    for s_e in start_end:
        for u_gpu in use_GPU:
            for codec in codecs:
                vc = VideoControl(video_in_list=video_in)
                vc.encoding_videos(s_e, u_gpu, codec)
