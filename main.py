import os
import pytz

from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from docx2pdf import convert
from dotenv import load_dotenv
from functools import partial

load_dotenv()

one_drive = os.getenv("OneDrive", None)
if not one_drive:
    raise ValueError("OneDrive environment variable not found.")

tz_name = os.getenv("TIME_ZONE", "America/New_York")
LOCAL_TIME_ZONE = ZoneInfo(tz_name)
UTC_TIME_ZONE = pytz.utc
LONG_DATE_FORMAT = os.getenv("LONG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S %Z")
ARCHIVE_DATE_FORMAT = os.getenv("ARCHIVE_DATE_FORMAT", "_%Y%m%d__%H-%M_%S")

INPUT_DIR = Path(one_drive) / os.getenv("INPUT_DIR", r"WorkStuff\resume\docx")
OUTPUT_DIR = Path(one_drive) / os.getenv("INPUT_DIR", r"WorkStuff\resume\pdf")
ARCHIVE_DIR = Path(one_drive) / os.getenv("INPUT_DIR",
                                          r"WorkStuff\resume\archive")
