import logging

from core.config import settings


logger = logging.Logger("DepositAPI Logger")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(settings.LOGS_PATH, encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel("INFO")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel("ERROR")

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
