from dotenv import load_dotenv
import os
import subprocess
import re
import openai
from time import sleep
from urllib import request
import math
from github_utils import get_repo
from openai_utils import generate_html
from stablehorde import generate_image
from beautifulsoup import generate_images


# Load environment variables from .env file
load_dotenv()

# Load environment variables from .env file
load_dotenv()

# Set GitHub access token and repository name
GITHUB_ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
REPO_NAME = os.environ["GITHUB_REPO_NAME"]

# Set OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Set Stablehorde API key
STABLEHORDE_API_KEY = os.environ["STABLEHORDE_API_KEY"]

# Set prompt for OpenAI API
prompt_template = "I want you to create HTML code based on the input text: {}. Reply only with HTML code no other comments. Please include CSS for the page. For the images, the <img> tags must include at least two attributes: a style attribute with at least the heigh and width in pixel and a custom alt text attribute different for each image and with at least 100 words to describe the image."


def make_changes_and_push(repo, local_directory, commit_message, input_text):
    # Generate HTML content using OpenAI API
    prompt = prompt_template.format(input_text)
    html_content = generate_html(prompt)

    # Generate images using Stablehorde API
    html_content = generate_images(html_content, STABLEHORDE_API_KEY, local_directory)

    # Clone or pull the repository
    if os.path.exists(local_directory):
        subprocess.run(f"git -C {local_directory} pull", shell=True)
    else:
        subprocess.run(
            f"git clone {repo.git_url.replace('git://', f'https://{GITHUB_ACCESS_TOKEN}@')} {local_directory}", shell=True)

    # Add, commit, and push the changes
    with open(os.path.join(local_directory, "index.html"), "w") as f:
        f.write(html_content)
    subprocess.run(f"git -C {local_directory} add .", shell=True)
    subprocess.run(f'git -C {local_directory} commit -m "{commit_message}"', shell=True)
    subprocess.run(f"git -C {local_directory} push", shell=True)

if __name__ == "__main__":
    # Code to be executed when the script is run as the main program

    # Get input from user
    input_text = input("Enter text to generate HTML content: ")

    # Set up repository and commit message
    repo = get_repo(GITHUB_ACCESS_TOKEN, REPO_NAME)
    commit_message = f"Add HTML file based on input text: {input_text}"

    # Set up local directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    local_directory = os.path.join(script_directory, "cloned_repo")

    # Make changes and push to GitHub
    make_changes_and_push(repo, local_directory, commit_message, input_text)

