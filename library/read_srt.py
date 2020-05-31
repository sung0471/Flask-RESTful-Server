from library.directory_control import get_metadata_dir_path


def read_srt(file_name):
    # file_name=['misaeng.S1.E0001.srt']
    srt_file_dir = get_metadata_dir_path(file_name)

    srt_data = list()
    for srtFile in srt_file_dir:
        f = open(srtFile, 'r', encoding='UTF8')
        lines = f.readlines()
        f.close()

        srt_line = list()
        for idx, line in enumerate(lines):
            if (idx+1) % 4 == 2:
                srt_line.append(line[0:12])
            elif (idx+1) % 4 == 3:
                srt_line.append(line[0:5])
            elif (idx+1) % 4 == 0:
                srt_data.append(srt_line)
            else:
                pass
    return srt_data


if __name__ == '__main__':
    filename = ['misaeng.S1.E0001.srt']
    srtdata = read_srt(filename)

    print(srtdata[0:5])
