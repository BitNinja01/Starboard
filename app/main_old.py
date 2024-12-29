import os, sys
import zazzle
from tqdm import tqdm
import shutil
from utilities import SB_ASCII, SB_FILES, SB_VIDEO, SB_PROBE, log
from gui import SB_Main_Window
from PyQt6.QtWidgets import QApplication

# Initialize logging
zazzle.ZZ_Init.configure_logger(file_name="starboard", function_tracking=True)
log = zazzle.ZZ_Logging.log

if __name__ == "__main__":
    # Console blurb because go big or go home amirite
    SB_ASCII.print_intro_consol_blurb(text="STARBOARD", font="doom")
    print()

    # Set library file paths
    input_library_path = input(f"Folder to run on: ")

    # Ask the user what to do
    print("")
    print(f"What would you like to do?")
    move_on = False

    while move_on == False:
        print("")
        print(f"1 - Label media with bitrates in file names")
        print(f"2 - Optimize media with low bitrate 1080p versions")
        print(f"3 - Auto rename downloaded files")
        print(f"4 - Exit")

        choice = input()

        # Label all video media with it's bitrate
        if choice == "1":

            # Get all the video files in our given directory
            all_videos = []
            all_files = SB_FILES.get_all_files_recursively(input_library_path)

            for file in all_files:
                if os.path.isfile(file):
                    if file.endswith(".mkv") or file.endswith(".mp4"):
                        all_videos.append(file)

            # Find all the unlabeled videos in the library
            unlabeled_videos = SB_FILES.get_unlabeled_videos(all_videos)

            # If there are unlabeled videos, add their bitrate to their name
            if unlabeled_videos:
                for video in tqdm(unlabeled_videos, desc="Renaming files", unit="file", dynamic_ncols=True, leave=True, file=sys.stdout):
                    SB_FILES.add_bitrate_to_namespace(video)

        # Create optimized 720p versions of all videos in the specified directory
        elif choice == "2":
            movies_folder_files = SB_FILES.get_files_in_directory(input_library_path)

            # Get all the actual movie files
            for movie in movies_folder_files:
                video_files = SB_FILES.find_video_files_in_directory(movie)

                optimized = False

                for video in video_files:
                    if "optimized" in str(video):
                        optimized = True
                        break

                if optimized == False:
                    # Get the first video index
                    video = video_files[0]

                    # Figure out if this video is SDR or HDR
                    hdr_check = SB_VIDEO.video_hdr_check(video)

                    # Convert to the appropriate new video

                    if hdr_check:
                        SB_VIDEO.create_optimized_video_hdr_to_sdr(input_file=video, target_bitrate=7, bitrate_buffer=1)
                    else:
                        SB_VIDEO.create_optimized_video_sdr_to_sdr(input_file=video, target_bitrate=7, bitrate_buffer=1)

        # Create correct video/folder names for newly downloaded content
        elif choice == "3":
            movie_folders = SB_FILES.get_files_in_directory(input_library_path)

            # Separate folders and videos in the main input folder
            main_folder_video_files = [item for item in movie_folders if item.endswith((".mkv", ".mp4"))]
            movie_folders = [item for item in movie_folders if not item.endswith((".mkv", ".mp4"))]

            log(2, f"{movie_folders}")

            # Make folders for each video, and move the videos to their respective folders
            if main_folder_video_files:
                log(1, f"Found {len(main_folder_video_files)} in the main library folder.")
                for video in main_folder_video_files:
                    # Rename the file
                    base_name, detailed_name, final_name = SB_FILES.fix_base_movie_name(video)

                    # Create a properly named folder
                    target_folder = f"{input_library_path}\\{base_name}"
                    if not os.path.exists(target_folder):
                        os.mkdir(target_folder)
                        log(0, f"Created folder: {target_folder}")
                    else:
                        log(1, f"Folder '{target_folder}' already exists.")

                    # Move the renamed file to the folder
                    source_path = f"{input_library_path}\\{final_name}"  # Use the full path as-is
                    destination_path = os.path.join(target_folder, final_name)
                    log(1, f"Source path: {source_path}")
                    log(1, f"Destination path: {destination_path}")

                    if os.path.exists(destination_path):
                        log(1, f"File '{destination_path}' already exists. Skipping move.")
                    elif os.path.exists(source_path):
                        shutil.move(source_path, destination_path)
                        log(0, f"Moved {source_path} >>> {destination_path}")
                    else:
                        log(3, f"Source file '{source_path}' does not exist.")

            # Rename folders and their contents
            for movie_folder in movie_folders:
                log(1, f"Running scan/rename on {movie_folder}")
                videos = SB_FILES.find_video_files_in_directory(movie_folder)

                # Rename all the videos in the folder
                for video in videos:
                    base_name, detailed_name, final_name = SB_FILES.fix_base_movie_name(video)

                # Rename the main folder to match the videos
                SB_FILES.rename_files(movie_folder, f"{input_library_path}\\{base_name}")


        elif choice == "4":
            log(2, f"Exiting...")
            break
        else:
            print("Please enter a valid number")