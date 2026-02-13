import os
import pytz

from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from docx2pdf import convert
from dotenv import load_dotenv
from enum import StrEnum, auto, Enum
from functools import partial


def main() -> None:
    load_dotenv()

    one_drive = os.getenv("OneDrive", None)
    if not one_drive:
        raise ValueError("OneDrive environment variable not found.")

    tz_name = os.getenv("TIME_ZONE", "America/New_York")
    TIME_ZONES = {
        "local": ZoneInfo(tz_name),
        "utc": pytz.utc
    }
    LONG_DATE_FORMAT = os.getenv("LONG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S %Z")
    ARCHIVE_DATE_FORMAT = os.getenv("ARCHIVE_DATE_FORMAT", "_%Y%m%d__%H-%M_%S")

    INPUT_DIR = Path(one_drive) / os.getenv("INPUT_DIR",
                                            r"WorkStuff\resume\docx")
    OUTPUT_DIR = Path(one_drive) / os.getenv("OUTPUT_DIR",
                                             r"WorkStuff\resume\pdf")
    ARCHIVE_DIR = Path(one_drive) / os.getenv("ARCHIVE_DIR",
                                              r"WorkStuff\resume\archive")

    class DateZones(StrEnum):
        LOCAL = auto()
        UTC = auto()

    class DateFormat(Enum):
        LONG = LONG_DATE_FORMAT
        ARCHIVE = ARCHIVE_DATE_FORMAT
        SHORT = "%Y-%m-%d"
        TIME = "%H:%M:%S"

    def get_datetime(zone: DateZones = DateZones.UTC) -> datetime:
        return datetime.now(TIME_ZONES[zone.value.lower()])

    def get_datestr(zone: DateZones = DateZones.UTC,
                    format: DateFormat = DateFormat.LONG) -> str:
        now_datetime = get_datetime(zone=zone)
        return now_datetime.strftime(format=format.value)

    get_utc_datestr = partial(get_datestr, zone=DateZones.UTC)
    get_local_datestr = partial(get_datestr, zone=DateZones.LOCAL)

    def archive_old_resume() -> None:
        files: list[Path] = []
        for f in OUTPUT_DIR.glob("*.pdf", case_sensitive=False):
            files.append(f.absolute())
        archive_datestr = get_local_datestr(format=DateFormat.ARCHIVE)
        for f in files:
            f_archive_path = ARCHIVE_DIR / \
                f"{f.stem}{archive_datestr}{f.suffix}"
            f.copy(f_archive_path, preserve_metadata=True)
