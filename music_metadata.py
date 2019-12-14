#!/usr/bin/env python3
# TODO albumartexchange api, get max image size available
# TODO column for total size of metadata
# TODO skip shasum arg
# TODO track time vs metadata time

import applescript
import binascii
import csv
import datetime
import ffmpeg
import hashlib
import os
import pymediainfo

run_shasum = 0
csv_file = '/Users/username/Music/Metadata/music_metadata.csv'
file_types = '.alac', '.aac', '.aiff', '.m4a', '.mp3', '.wav'
music_dir = '/Users/username/Music/iTunes/iTunes Media/Music'
cover_dir = '/Users/username/Music/Metadata/Covers/'
def write_header():
    print('[mm] opening new csv file')
    with open(csv_file, 'w') as fp:
        header_writer = csv.writer(fp)
        print('[mm] writing csv header')
        header_writer.writerow(["Artist", "Track", "Album", "Image Codec", "Image Size (KiB)", "Width (px)",
                                "Height (px)", "Not Square", "Audio Codec", "Encoder", "Bit Rate (kbps)",
                                "Sample Rate (kHz)", "Sample Format", "Channels", "Duration (h:m:s)",
                                "Media Type", "Filename", "File Path", "sha256sum", "Writing Library", "Bit Rate Mode",
                                "Bit Depth", "Tagged Date"])


def main():
    for dirpath, dirnames, filenames in os.walk(music_dir):
        for track_file in filenames:
            if track_file.endswith(file_types):  # check for extensions
                track_file_with_path = (os.path.join(dirpath, track_file))
                print('[mm] extracting metadata from: ' + track_file)

                # probe the file for info
                probe = ffmpeg.probe(track_file_with_path)

                # extract metadata tags
                tags = probe['format']['tags']

                album = tags.get('album')
                artist = tags.get('artist')
                encoder = tags.get('encoder')
                media = tags.get('MEDIA')
                title = tags.get('title')

                # extract audio tags
                audio = probe['streams'][0]

                audio_codec = audio['codec_long_name']
                bit_rate = float(audio['bit_rate']) // 1024  # floor divide by 1024 to get rounded kbps
                channels = int(audio['channels'])
                duration = str(datetime.timedelta(seconds=round(float(audio['duration']))))  # convert seconds to h/m/s
                sample_fmt = str(audio['sample_fmt'])
                sample_rate = int(audio['sample_rate']) // 1000  # floor divide by 1000 to get khz
                # extract video/image tags
                video = probe['streams'][1]

                height = video['height']
                video_codec = video['codec_long_name']
                width = video['width']
                if width != height:
                    not_square = 1
                else:
                    not_square = 0
                media_info = pymediainfo.MediaInfo.parse(track_file_with_path, cover_data=True)
                first_track = media_info.tracks[0]
                writing_library = first_track.writing_library

                second_track = media_info.tracks[1]
                bit_rate_mode = second_track.bit_rate_mode
                bit_depth = second_track.bit_depth
                tagged_date = second_track.tagged_date
                try:
                    decoded_cover = binascii.a2b_base64(first_track.cover_data)
                    image_size = len(decoded_cover) // 1024  # floor divide by 1024 to get kbytes
                    #os.system('ffmpeg -y -i ' + "\"" + track_file_with_path + "\"" + ' -an -vcodec copy ' + cover_dir + "\"" + album + "\"" + '.jpg')
                except:
                    image_size = 0
                if run_shasum == 1:
                    # generate sha256sums
                    with open(track_file_with_path, 'rb') as f:
                        track_bytes = f.read()
                        sha_sum = hashlib.sha256(track_bytes).hexdigest()
                else:
                    sha_sum = 0
                # write values to csv file
                with open(csv_file, 'a') as fp:
                    writer = csv.writer(fp)
                    writer.writerow(
                        [artist, title, album, video_codec, image_size, width, height, not_square, audio_codec, encoder, bit_rate,
                         sample_rate, sample_fmt, channels, duration, media, track_file, f'"{track_file_with_path}"',
                         sha_sum, writing_library, bit_rate_mode, bit_depth, tagged_date])
            else:
                print('[mm] ' + track_file + ' is not a music file!')


write_header()
main()
print('[mm] finished')

