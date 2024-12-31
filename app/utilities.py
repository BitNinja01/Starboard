import os
from pyfiglet import Figlet
import zazzle
import subprocess
import json
import ffmpeg
from datetime import datetime
import shutil

# Initialize logging
zazzle.ZZ_Init.configure_logger(file_name="starboard")
log = zazzle.ZZ_Logging.log

class SB_EXECUTE:
    def get_movie_folders(input_library_path):
        movie_folders = SB_FILES.get_files_in_directory(input_library_path)

        # Separate folders and videos in the main input folder
        main_folder_video_files = [item for item in movie_folders if item.endswith((".mkv", ".mp4"))]
        movie_folders = [item for item in movie_folders if not item.endswith((".mkv", ".mp4"))]

        log(2, f"{movie_folders}")
        return movie_folders

class SB_ASCII:
    def print_intro_consol_blurb(text, font):
        font = Figlet(font=f"{font}")
        log(1, font.renderText(f"{text}"), flag=False)

class SB_FILES:

    def parse_movie_name(movie_path):

        log(1, f"Parsing file name : {movie_path}")

        # Get just the folder name of the full movie path
        folder_name = movie_path.rpartition("\\")[2]
        log(0, f"Folder: {folder_name}")

        # Get the year of the movie from it's file name
        movie_year = SB_FILES.find_video_year_from_name(folder_name)
        log(0, f"Year : {movie_year}")

        # Get the front of our string
        name_front = folder_name.rpartition(str(movie_year))[0]
        log(0, f"Name Front : {name_front}")

        # Get the back of our string
        name_back = folder_name.rpartition(str(movie_year))[1]
        log(0, f"Name Back : {name_back}")

        # Combine the front and back
        base_name = f"{name_front}{name_back}"
        log(0, f"Front + Back : {base_name}")

        # Replace any periods with spaces
        base_name = base_name.replace(".", " ")
        log(0, f"Replaced '.' : {base_name}")

        # Fix any 'vs' in our title
        base_name = base_name.replace(" vs ", " vs.")
        log(0, f"VS fix : {base_name}")

        # Remove and re-add the () to the year
        base_name = base_name.replace("(", "")
        base_name = base_name.replace(")", "")
        base_name = base_name.replace(str(movie_year), f"({str(movie_year)})")
        log(0, f"Fix () : {base_name}")

        # SB_FILES.rename_files(full_movie_path, f"{folder_name}\\{final_name}")

        return base_name

    def parse_video_name(video_path, parsed_movie_name=None, get_resolution=False, get_bitrate=False,
                         get_dynamic_range=False):

        # Get the movie extension
        movie_extension = video_path[-4:]
        log(0, f"Extension : {movie_extension}")

        # If we didn't pass a parsed movie name, then we need to parse it
        if parsed_movie_name == None:
            file_name = video_path.rpartition("\\")[-1]
            folder_name = video_path.rpartition("\\")[0]
            log(0, f"Folder: {folder_name}")
            log(0, f"Movie : {file_name}")

            # Get the year of the movie from it's file name
            movie_year = SB_FILES.find_video_year_from_name(file_name)
            log(0, f"Year : {movie_year}")

            # Get the front of our string
            name_front = file_name.rpartition(str(movie_year))[0]
            log(0, f"Name Front : {name_front}")

            # Get the back of our string
            name_back = file_name.rpartition(str(movie_year))[1]
            log(0, f"Name Back : {name_back}")

            # Combine the front and back
            base_name = f"{name_front}{name_back}"
            log(0, f"Front + Back : {base_name}")

            # Replace any periods with spaces
            base_name = base_name.replace(".", " ")
            log(0, f"Replaced '.' : {base_name}")

            # Fix any 'vs' in our title
            base_name = base_name.replace(" vs ", " vs.")
            log(0, f"VS fix : {base_name}")

            # Remove and re-add the () to the year
            base_name = base_name.replace("(", "")
            base_name = base_name.replace(")", "")
            base_name = base_name.replace(str(movie_year), f"({str(movie_year)})")
            log(0, f"Fix () : {base_name}")
            parsed_video_name = base_name

        # Use the parsed movie name as the base name for the video we're working on
        else:
            parsed_video_name = parsed_movie_name

        # Make a list of details to add to the video name
        details = []

        # Add video width and height
        if get_resolution:
            media_dimensions = SB_PROBE.get_video_dimensions(video_path)
            resolution = media_dimensions[0] / 1.77777
            resolution = int(resolution)

            log(0, f"Resolution : {media_dimensions}")
            details.append(f".{resolution}")

        # Add HDR status
        if get_dynamic_range:
            dynamic_resolution = SB_VIDEO.video_hdr_check(video_path)
            if dynamic_resolution == True:
                log(0, f"HDR")
                details.append(f".HDR")
            else:
                log(0, f"SDR")
                details.append(f".SDR")

        # Add the bitrate
        if get_bitrate:
            bitrate = SB_VIDEO.get_video_bitrate_ffmpeg(video_path)
            mbps = SB_VIDEO.convert_bitrate_to_mbps(bitrate)
            log(0, f"Bitrate : {bitrate}Mbps")
            details.append(f".{bitrate}Mbps")

        if details:
            for detail in details:
                parsed_video_name = f"{parsed_movie_name}{detail}"

        # Add extension back in
        parsed_video_name = f"{parsed_video_name}{movie_extension}"
        log(0, f"Add extension : {parsed_video_name}")

        # SB_FILES.rename_files(full_movie_path, f"{folder_name}\\{final_name}")

        return parsed_video_name

    def fix_base_show_name():
        pass

    def add_media_data_to_filename(full_file_path):

        # Get video HDR status
        HDR = SB_VIDEO.video_hdr_check(full_file_path)

        # Get bitrate
        bitrate = SB_VIDEO.get_video_bitrate_ffmpeg(full_file_path)

    def get_video_bitrate_from_file_name(video_path):
        log(1, f"Getting bitrate for : {video_path}")

        # Split the string until we're left with the Mbps, and then convert it to a float
        left_string = video_path.rpartition("Mbps")[0]
        mbps = left_string.rpartition(".")[-1]
        mbps = mbps.replace(",", ".")
        mbps = float(mbps)

        log(0, f"Bitrate : {mbps}Mbps")

    # Get a list of years from the first movie ever released to the current year
    def create_list_of_years():
        log(1, f"Creating list of years from 1888 - {datetime.now().year}")
        current_year = datetime.now().year
        years_list = []

        # current_year + 1

        for i in range(1888, 2100):
            years_list.append(i)

        return years_list

    def create_list_of_show_episode_strings():
        # Possible string combinations

        possible_strings_no_spaces = []
        possible_strings_periods = []
        possible_strings_spaces = []

        strings_list = [
            "E",
            "EP",
            "e",
            "ep",
            "EPI",
            "epi",
            "EPISODE",
            "episode",
            "Episode"
        ]

        numbers_list = []
        for number in range(9):
            numbers_list.append(f"{0}{number}")

        for string in strings_list:
            possible_strings_no_spaces.append(f"{string}{number}")


    def find_video_year_from_name(video_name):
        years = SB_FILES.create_list_of_years()

        log(1, f"Finding year for : {video_name}")

        # Find the year as long as it doesn't equal 1080 or 2160
        for i in years:
            if str(i) in video_name:
                if i != 1080 and i != 2160:
                    year = i
                    break

        return year

    def fix_downloaded_names(download_directory):
        pass

    def rename_files(old_name, new_name):
        log(1, f"Renaming : {old_name} >>> {new_name}")

        old_drive, old_path = os.path.splitdrive(old_name)
        new_drive, new_path = os.path.splitdrive(new_name)
        log(0, f"Old Drive : {old_drive}")
        log(0, f"Old Path  : {old_path}")
        log(0, f"New Drive : {new_drive}")
        log(0, f"New Path  : {new_path}")

        if old_drive == new_drive:
            # Same drive: Use os.rename
            os.rename(old_name, new_name)
        else:
            # Different drives: Create new folder, move contents, and delete old folder
            log(1, f"Cross-drive rename detected.")
            os.makedirs(new_name, exist_ok=True)  # Create new folder
            for item in os.listdir(old_name):
                shutil.move(os.path.join(old_name, item), new_name)  # Move contents
            os.rmdir(old_name)  # Remove old folder

    def get_unlabeled_videos(video_list):
        log(1, f"Getting unlabeled videos...")
        videos_not_labeled = []
        for video in video_list:
            # fix any borked names
            if "NoneMbps" in video:
                SB_FILES.rename_files(video, video.replace("NoneMbps.", ""))

            # Find the videos already named
            end_of_file = video[-13:]
            if "Mbps" in end_of_file:
                log(0, f"Namespace already in: {video}")
            else:
                videos_not_labeled.append(video)

        for video in videos_not_labeled:
            log(0, f"{video}")

        return(videos_not_labeled)

    def add_bitrate_to_namespace(file_path):
        log(1, f"Adding namespace to {file_path}")

        log(0, f"Getting bitrate...")
        bitrate = SB_VIDEO.get_video_bitrate_ffmpeg(file_path)
        mbps = SB_VIDEO.convert_bitrate_to_mbps(bitrate_bps=bitrate)
        log(0, f"Bitrate: {mbps}")

        extension = file_path[-4:]
        new_front = file_path.replace(extension, "")
        mbps = str(mbps).replace(".", ",")
        mbps = f".{mbps}Mbps"
        new_name = f"{new_front}{mbps}{extension}"

        SB_FILES.rename_files(file_path, new_name)

    def get_files_in_directory(directory):
        log(1, f"Getting all files in directory: {directory}...")
        file_names = os.listdir(directory)
        log(2, f"{file_names}")

        file_paths = []
        if file_names != None:
            for name in file_names:
                file_paths.append(os.path.join(directory, name))

        for path in file_paths:
            log(0, f"{path}")

        return file_paths

    def get_all_files_recursively(directory):
        all_files = []
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if os.path.isdir(full_path):
                # Recur for subdirectories
                all_files.extend(SB_FILES.get_all_files_recursively(full_path))
            elif os.path.isfile(full_path):
                all_files.append(full_path)
        return all_files

    def find_video_files_in_directory(directory):
        log(1, f"Getting all video files in directory: {directory}")
        video_paths = []
        files = os.listdir(directory)
        for file in files:
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path):
                if full_path.endswith(".mp4") or full_path.endswith(".mkv"):
                    video_paths.append(os.path.join(directory, file))

        for path in video_paths:
            log(0, path)

        return video_paths

class SB_PROBE:

    def get_video_dimensions(file_path):
        try:
            log(1, f"Getting resolution for {file_path}")
            # Run ffprobe to get width and height
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "json", file_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Parse the JSON output
            metadata = json.loads(result.stdout)
            streams = metadata.get("streams", [])
            if streams:
                width = streams[0].get("width")
                height = streams[0].get("height")
                log(0, f"{width}x{height}")
                return width, height
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

class SB_VIDEO:
    def get_video_bitrate_ffmpeg(file_path):
        try:
            # Run ffprobe to get metadata as JSON
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                 'format=bit_rate', '-of', 'json', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Parse the JSON output
            metadata = json.loads(result.stdout)
            return int(metadata['format']['bit_rate']) if 'format' in metadata and 'bit_rate' in metadata[
                'format'] else None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def video_hdr_check(file_path):
        try:
            # Run ffprobe to extract color metadata
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=color_primaries,transfer_characteristics,matrix_coefficients",
                    "-of", "json", file_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Parse the JSON output
            metadata = json.loads(result.stdout)
            streams = metadata.get("streams", [])

            if not streams:
                return False

            # Check color metadata
            video_stream = streams[0]
            color_primaries = video_stream.get("color_primaries", "")
            transfer_characteristics = video_stream.get("transfer_characteristics", "")
            matrix_coefficients = video_stream.get("matrix_coefficients", "")

            # Identify HDR characteristics
            if transfer_characteristics in ["smpte2084", "arib-std-b67"]:  # PQ or HLG
                return True
            elif color_primaries == "bt2020":
                return True
            else:
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def convert_bitrate_to_mbps(bitrate_bps):
        if bitrate_bps is None:
            return None
        # Divide by 1,000,000 to get Mbps
        return round(bitrate_bps / 1_000_000, 2)

    def create_optimized_video_sdr_to_sdr(input_file, target_bitrate, bitrate_buffer):
        log(1, f"Converting SDR video to SDR video...")
        log(0, f"Input file: {input_file}")

        # ffmpeg command to convert MKV to MP4 with target bitrate
        ffmpeg.input(f'{input_file}') \
            .video.filter('scale', '-2', '720') \
            .output(f'{input_file.replace(".mkv", "")}.optimized.mp4', vcodec='libx265', preset='superfast', acodec='copy', **{'b:v': f'{target_bitrate}M', 'maxrate': target_bitrate, 'bufsize': f'{bitrate_buffer}M'}) \
            .run(overwrite_output=True)

    def create_optimized_video_hdr_to_sdr(input_file, target_bitrate, bitrate_buffer):
        log(1, f"Converting HDR video to SDR video...")
        log(0, f"Input file: {input_file}")

        # ffmpeg command to convert MKV to MP4 with target bitrate
        try:
            log(0, f"Attempting to convert HDR video using 'bt709' colorspace...")
            ffmpeg.input(f'{input_file}') \
                .video.filter('zscale', t='linear', npl=100) \
                .filter('scale', '-2', '720') \
                .filter('format', pix_fmts='gbrpf32le') \
                .filter('tonemap', tonemap='hable', desat=0) \
                .filter('zscale', p='bt709', t='bt709', m='bt709', r='tv') \
                .filter('format', pix_fmts='yuv420p') \
                .output(f'{input_file.replace(".mkv", "")}.optimized.mp4', vcodec='libx265', preset='superfast', scodec='copy', acodec='aac', audio_bitrate='128k', **{'b:v': f'{target_bitrate}M', 'maxrate': target_bitrate, 'bufsize': f'{bitrate_buffer}M'}) \
                .run(overwrite_output=True)

            # libx265
            # tune='fastdecode'
        except:
            log(3, f"Unable to convert HDR video to SDR video")
            log(2, f"Converting using SDR to SDR...")
            SB_VIDEO.create_optimized_video_sdr_to_sdr(input_file=input_file, target_bitrate=target_bitrate, bitrate_buffer=bitrate_buffer)