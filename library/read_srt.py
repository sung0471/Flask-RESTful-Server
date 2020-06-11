from library.directory_control import get_file_dir_path


def read_srt(srt_file_dir):
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
    file_path = get_file_dir_path(filename, ['metadata', 'lifecycle'])
    srtdata = read_srt(file_path)

    print(srtdata[0:5])
