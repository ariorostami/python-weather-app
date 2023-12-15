from weather import *
from utils import *


def main():
    # Log configuration
    logger.add(LOG_FILE_PATH, rotation="500 MB", level="INFO")
    create_gui(API_KEY)

if __name__ == "__main__":
    main()