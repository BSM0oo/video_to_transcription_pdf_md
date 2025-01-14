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

def get_working_dir():
    home = os.path.expanduser("~")
    downloads_docs_dir = os.path.join(home, "Documents", "Downloads Documents")
    working_dir = os.path.join(downloads_docs_dir, "Video_to_PDF_output")
    
    if not os.path.exists(downloads_docs_dir):
        os.makedirs(downloads_docs_dir)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    return working_dir

def process_video(video_file, method="1", param=0.5, extract_text=True):
    """Process video file with given parameters"""
    if not os.path.isfile(video_file):
        raise ValueError("File does not exist")

    working_dir = get_working_dir()
    output_dir = os.path.join(working_dir, "frames_output")
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    if method == "1":
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', video_file,
            '-vf', f'fps=1/{param}',
            os.path.join(output_dir, 'frame%04d.png')
        ]
    else:
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', video_file,
            '-vf', f"select='gt(scene,{param})'",
            '-vsync', 'vfr',
            os.path.join(output_dir, 'frame%04d.png')
        ]

    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    if not os.listdir(output_dir):
        raise Exception("No frames were extracted. Try adjusting the parameters.")

    pdf_file = os.path.join(working_dir, 'output.pdf')
    compile_pdf(output_dir, pdf_file)

    if extract_text:
        text_content = extract_text_from_images(output_dir)
        md_file = os.path.join(working_dir, 'output.md')
        with open(md_file, 'w') as f:
            f.write(text_content)

    shutil.rmtree(output_dir)
    return working_dir