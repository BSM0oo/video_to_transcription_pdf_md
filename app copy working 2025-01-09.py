import subprocess
import os
import sys
import shutil
import pytesseract
from PIL import Image
import pyperclip

def check_command(command):
    if shutil.which(command) is None:
        print(f"Error: {command} is not installed or not in PATH.")
        sys.exit(1)

def extract_text_from_images(image_dir):
    print("Extracting text from images using OCR...")
    text_content = ""
    image_files = sorted([
        os.path.join(image_dir, img)
        for img in os.listdir(image_dir)
        if img.endswith('.png') or img.endswith('.jpg')
    ])
    for img_path in image_files:
        print(f"Processing {img_path}...")
        try:
            img = Image.open(img_path)
            # Optionally preprocess the image for better OCR accuracy
            img = img.convert('L')  # Convert to grayscale
            # img = img.point(lambda x: 0 if x < 128 else 255, '1')  # Binarize image
            text = pytesseract.image_to_string(img)
            text_content += text + "\n\n"
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
    return text_content

def get_resource_path():
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return base_path

def create_working_dir():
    # Use Documents/Downloads Documents folder
    home = os.path.expanduser("~")
    downloads_docs_dir = os.path.join(home, "Documents", "Downloads Documents")
    working_dir = os.path.join(downloads_docs_dir, "Video_to_PDF_output")
    
    # Create Downloads Documents directory if it doesn't exist
    if not os.path.exists(downloads_docs_dir):
        os.makedirs(downloads_docs_dir)
        
    # Create Video_to_PDF_output directory
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    print(f"Output will be saved to: {working_dir}")
    return working_dir

def compile_pdf(output_dir, pdf_file):
    print("Compiling images into PDF...")
    try:
        convert_cmd = [
            'convert',
            '-density', '300',
            os.path.join(output_dir, 'frame*.png'),
            pdf_file
        ]
        result = subprocess.run(convert_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error creating PDF: {result.stderr}")
            print("\nTroubleshooting tips:")
            print("1. Check if ImageMagick is installed: brew install imagemagick")
            print("2. You may need to edit ImageMagick policy:")
            print("   sudo nano /opt/homebrew/etc/ImageMagick-7/policy.xml")
            print("   Change: <policy domain=\"coder\" rights=\"none\" pattern=\"PDF\" />")
            print("   To: <policy domain=\"coder\" rights=\"read|write\" pattern=\"PDF\" />")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def open_folder(path):
    """Open the folder in Finder"""
    try:
        subprocess.run(['open', path])
    except Exception as e:
        print(f"Could not open folder: {e}")

def main():
    # Get working directory
    working_dir = create_working_dir()
    
    # Check if required commands are installed
    check_command('ffmpeg')
    check_command('convert')  # ImageMagick's convert command

    # Check if Tesseract is installed
    if shutil.which('tesseract') is None:
        print("Error: Tesseract-OCR is not installed or not in PATH.")
        sys.exit(1)

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
    output_dir = os.path.join(working_dir, "frames_output")
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

    # Compile images into PDF with higher density
    pdf_file = os.path.join(working_dir, 'output.pdf')
    compile_pdf(output_dir, pdf_file)

    print(f"\nPDF saved as {pdf_file}")

    # Ask if user wants to extract text
    extract_text = input("Do you want to extract text from the images? (y/n): ").lower()
    if extract_text == 'y':
        text_content = extract_text_from_images(output_dir)
        # Ask user whether to copy to clipboard or save as markdown file
        print("\nChoose an option:")
        print("1. Copy text to clipboard")
        print("2. Save text as a Markdown file")
        option = input("Enter 1 or 2: ")

        if option == '1':
            pyperclip.copy(text_content)
            print("Text has been copied to the clipboard.")
        elif option == '2':
            md_file = os.path.join(working_dir, 'output.md')
            with open(md_file, 'w') as f:
                f.write(text_content)
            print(f"Text has been saved as {md_file}")
        else:
            print("Invalid option. Skipping text extraction.")

    # Optionally, clean up extracted frames
    cleanup = input("Do you want to delete the extracted frames? (y/n): ")
    if cleanup.lower() == 'y':
        shutil.rmtree(output_dir)
        print("Cleaned up extracted frames.")
    else:
        print(f"Extracted frames are saved in the directory: {output_dir}")

    # Open the output folder in Finder
    print("\nOpening output folder...")
    open_folder(working_dir)

if __name__ == '__main__':
    main()