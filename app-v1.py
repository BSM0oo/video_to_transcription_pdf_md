import subprocess
import os
import sys
import shutil

def check_command(command):
    if shutil.which(command) is None:
        print(f"Error: {command} is not installed or not in PATH.")
        sys.exit(1)

def main():
    # Check if ffmpeg and convert are installed
    check_command('ffmpeg')
    check_command('convert')

    # Get video file path
    video_file = input("Enter the path to the video file: ").strip('"')

    # Check if file exists
    if not os.path.isfile(video_file):
        print("File does not exist.")
        sys.exit(1)

    # Ask user for extraction method
    print("\nChoose extraction method:")
    print("1. Fixed intervals")
    print("2. Scene change detection")
    method = input("Enter 1 or 2: ")

    # Create output directory
    output_dir = "frames_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        # Clear the output directory if it already exists
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)

    if method == '1':
        # Fixed intervals
        interval = input("Enter time interval between screenshots (in seconds, e.g., 0.5): ")

        # Validate interval input
        try:
            interval = float(interval)
            if interval <= 0:
                raise ValueError
        except ValueError:
            print("Invalid interval. Please enter a positive number.")
            sys.exit(1)

        # Construct ffmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', video_file,
            '-vf', f'fps=1/{interval}',
            os.path.join(output_dir, 'frame%04d.png')
        ]

    elif method == '2':
        # Scene change detection
        threshold = input("Enter scene change threshold (default is 0.3): ")
        threshold = threshold.strip()
        if threshold == '':
            threshold = '0.3'

        # Validate threshold input
        try:
            threshold = float(threshold)
            if not 0 <= threshold <= 1:
                raise ValueError
        except ValueError:
            print("Invalid threshold. Please enter a number between 0 and 1.")
            sys.exit(1)

        # Construct ffmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', video_file,
            '-vf', f"select='gt(scene,{threshold})'",
            '-vsync', 'vfr',
            os.path.join(output_dir, 'frame%04d.png')
        ]
    else:
        print("Invalid option.")
        sys.exit(1)

    # Run ffmpeg command
    print("\nExtracting frames...")
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # Check if frames were extracted
    if not os.listdir(output_dir):
        print("No frames were extracted. Try adjusting the parameters.")
        sys.exit(1)

    # Compile images into PDF
    print("Compiling images into PDF...")
    # Compile images into PDF with higher density
    print("Compiling images into PDF...")
    pdf_file = 'output.pdf'
    convert_cmd = [
        'convert',
        '-density', '300',  # Set the density to 300 DPI
        os.path.join(output_dir, 'frame*.png'),
        pdf_file
    ]
    subprocess.run(convert_cmd)

    print(f"\nPDF saved as {pdf_file}")

    # Optionally, clean up extracted frames
    cleanup = input("Do you want to delete the extracted frames? (y/n): ")
    if cleanup.lower() == 'y':
        shutil.rmtree(output_dir)
        print("Cleaned up extracted frames.")
    else:
        print(f"Extracted frames are saved in the directory: {output_dir}")

if __name__ == '__main__':
    main()