import os
import zazzle
import subprocess
import json
import ffmpeg
from datetime import datetime
import shutil
import imdb

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

    def parse_video_name(video_path, parsed_movie_name=None, get_resolution=False, get_video_bitrate=False,
                         get_audio_codec=False, get_dynamic_range=False, get_video_framerate=False,
                         get_video_colorspace=False, get_imdb_id=False):

        metadata = SB_PROBE.get_video_metadata(video_path)
        log(0, f"Metadata : {metadata}")

        # Get the movie extension
        movie_extension = video_path[-4:]
        log(0, f"Extension : {movie_extension}")

        # If we didn't pass a parsed movie name, then we need to parse it from the file path
        file_name = video_path.rpartition("\\")[-1]
        folder_name = video_path.rpartition("\\")[0]
        log(0, f"Folder: {folder_name}")
        log(0, f"Movie : {file_name}")

        # Figure out if the video is a special edition or whatever
        edition = SB_FILES.detect_special_edition(file_name)

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

        if " vs " in base_name:
            # Fix any 'vs' in our title
            base_name = base_name.replace(" vs ", " vs.")
            log(0, f"VS fix : {base_name}")

        # Remove and re-add the () to the year
        base_name = base_name.replace("(", "")
        base_name = base_name.replace(")", "")
        base_name = base_name.replace(str(movie_year), f"({str(movie_year)})")
        log(0, f"Fix () : {base_name}")
        parsed_video_name = base_name

        # Get the IMDB ID
        if get_imdb_id:
            imdb_tag = SB_IMDB.imdb_get_id_from_title(parsed_video_name)
            log(0, f"IMDB ID : {id}")

        # Make a list of details to add to the video name
        details = []

        # Add video width and height
        if get_resolution:
            resolution = SB_PROBE.get_video_resolution(video_path)

            log(0, f"Resolution : {resolution}")
            details.append(f".{resolution}")

        # Add HDR status
        if get_dynamic_range:
            dynamic_range = SB_PROBE.get_video_hdr_status(video_path)
            if dynamic_range == True:
                log(0, f"HDR")
                details.append(f".HDR")
            else:
                log(0, f"SDR")
                details.append(f".SDR")

        # Add the video bitrate
        if get_video_bitrate:
            bitrate = SB_PROBE.get_video_bitrate(video_path)
            mbps = SB_PROBE.convert_bitrate_to_mbps(bitrate)
            log(0, f"Bitrate : {bitrate}Mbps")
            mbps = str(mbps).replace(".", ",")
            details.append(f".{mbps}Mbps")

        # Add the audio codec
        if get_audio_codec:
            audio_codec = SB_PROBE.get_audio_codec(video_path)
            details.append(f".{audio_codec}")

        # Add the video framerate
        if get_video_framerate:
            video_framerate = round(SB_PROBE.get_video_fps(video_path), 2)
            video_framerate = str(video_framerate).replace(".", ",")
            details.append(f".{video_framerate}fps")

        # Get the video colorspace
        if get_video_colorspace:
            video_colorspace = SB_PROBE.get_video_colorspace(video_path)
            details.append(f".{video_colorspace}")

        # If we want to add any details to the end of our file names, add them
        if details:
            for detail in details:
                parsed_video_name = f"{parsed_video_name}{detail}"

        # Add IMDB tag to name
        if get_imdb_id:
            parsed_video_name = parsed_video_name + " {imdb -" + imdb_tag + "}"

        # If we detected an edition, add it to the end before the extension
        if edition:
            edition = edition.title()
            parsed_video_name = parsed_video_name + " {edition-" + edition + "}"

        # Add extension back in
        parsed_video_name = f"{parsed_video_name}{movie_extension}"
        log(0, f"Add extension : {parsed_video_name}")

        return parsed_video_name

    def detect_special_edition(file_name):

        log(1, f"Looking for editions for {file_name}")

        # Convert name to lowercase and get rid of punctuation for easier checks
        file_name = file_name.lower()
        file_name = file_name.replace("_", " ").replace(".", " ").replace("'", "").replace(":", " ").replace(";", " ")

        # Special edition keywords
        normalized_keywords = {
            "directors": ["directors", "directors cut", "directorscut"],
            "extended": ["extended", "extendededition"],
            "remastered": ["remastered", "redux", "remaster"],
            "special edition": ["special edition", "deluxe", "specialedition", "collectorsedition", "collectors "
                                                                                                    "edition"]
        }

        # Figure out what special edition we've got
        editions = []
        for keyword, variations in normalized_keywords.items():
            for variation in variations:
                if variation in file_name:
                    editions.append(keyword)

        if len(editions) > 1:
            log(2, f"{len(editions)} editions detected in {file_name}")
            log(0, f"Using first edition : {editions[0]}")
        elif len(editions) == 1:
            log(1, f"1 edition detected : {editions[0]}")
            return editions[0]
        else:
            return None

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

    def get_video_resolution(video_path):
        media_dimensions = SB_PROBE.get_video_dimensions(video_path)
        resolution = media_dimensions[0] / 1.77777
        resolution = int(resolution)
        return resolution

    def get_video_bitrate(file_path):
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

    def convert_bitrate_to_mbps(bitrate_bps):
        if bitrate_bps is None:
            return None
        # Divide by 1,000,000 to get Mbps
        return round(bitrate_bps / 1_000_000, 2)

    def get_video_hdr_status(file_path):
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

    def get_audio_codec(file_path):
        try:
            # Run ffprobe to get audio codec
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
                 'stream=codec_name', '-of', 'json', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Parse the JSON output
            metadata = json.loads(result.stdout)
            return metadata['streams'][0]['codec_name'] if metadata.get('streams') else None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_video_fps(file_path):
        try:
            # Run ffprobe to get video frame rate
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                 'stream=avg_frame_rate', '-of', 'json', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Parse the JSON output
            metadata = json.loads(result.stdout)
            if metadata.get('streams'):
                avg_frame_rate = metadata['streams'][0]['avg_frame_rate']
                return eval(avg_frame_rate) if avg_frame_rate else None
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_video_colorspace(file_path):
        try:
            # Run ffprobe to get video colorspace
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                 'stream=color_space', '-of', 'json', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Parse the JSON output
            metadata = json.loads(result.stdout)
            return metadata['streams'][0]['color_space'] if metadata.get('streams') and 'color_space' in \
                                                            metadata['streams'][0] else None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_video_metadata(file_path):
        try:
            if not os.path.exists(file_path):
                log(3, f"Error: File not found at {file_path}")
                return None

            # Run ffprobe to extract tags
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=tags', '-of', 'json', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Parse the JSON output
            metadata = json.loads(result.stdout)
            if 'format' in metadata and 'tags' in metadata['format']:
                return metadata['format']['tags']
            else:
                log(3, "No tags found in the file.")
                return None
        except:
            log(4, f"CRITICAL ERROR")
            return None

class SB_IMDB:
    def imdb_get_id_from_title(title):
        ia = imdb.Cinemagoer()
        movies = ia.search_movie(title)
        if movies:
            movie = movies[0]  # Get the first result
            log(0, f"Movie ID : {movie.movieID}")
            return movie.movieID
        else:
            log(3, f"No results found for '{title}'")
        return None

    def imdb_get_year_from_id(id):
        pass

    def imdb_get_description_from_id(id):
        pass

class SB_VIDEO:
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