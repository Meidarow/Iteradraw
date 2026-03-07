import logging
import sys

def configure_logger():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    file = logging.FileHandler('log.txt')
    file.setFormatter(formatter)

    root.addHandler(console)
    root.addHandler(file)

