import os
import subprocess
from github import Github
from dotenv import load_dotenv

def run_command(command):
    try:
        process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Success: {process.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def unstage_folders(folders_to_remove):
    """Unstage specific folders from git."""
    for folder in folders_to_remove:
        if run_command(f"git rm -r --cached {folder}"):
            print(f"Successfully unstaged {folder}")
        else:
            print(f"Failed to unstage {folder}")

def setup_repository(repo_name: str, description: str = ""):
    # Load GitHub token from environment
    load_dotenv()
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("Please set GITHUB_TOKEN in your environment variables")
        return False

    try:
        # Create GitHub repository
        g = Github(github_token)
        user = g.get_user()
        repo = user.create_repo(repo_name, description=description, private=False)
        print(f"Created repository: {repo.html_url}")

        # Initialize git and push
        commands = [
            "git init",
            "git add .",
        ]
        
        # Add these lines after 'git add .'
        folders_to_remove = ["venv", "__pycache__"]  # Add your folders here
        unstage_folders(folders_to_remove)
        
        commands.extend([
            'git commit -m "Initial commit"',
            f"git remote add origin {repo.clone_url}",
            "git branch -M main",
            "git push -u origin main"
        ])

        for command in commands:
            if not run_command(command):
                return False

        print("Repository setup completed successfully!")
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    repo_name = "video-to-pdf"
    description = "A Python tool to convert video content to PDF format"
    setup_repository(repo_name, description)
