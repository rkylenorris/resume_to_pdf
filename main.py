import os
import pytz

from pathlib import Path
from docx2pdf import convert
from zoneinfo import ZoneInfo
from functools import partial
from dotenv import load_dotenv
from getpass import getuser
from enum import StrEnum, auto, Enum
from datetime import datetime, _TzInfo, tzinfo
from logging import getLogger, Handler

logger = getLogger(Path(__file__).parent.name)

load_dotenv()

ROOT_DIR: Path = Path(os.getenv("ROOT_DIR", f"{Path.home()}"))
if not ROOT_DIR.exists():
    logger.critical(f"Root directory '{ROOT_DIR.absolute()}' doesn't exist")
    exit(1)

RESUME_PATTERN = os.getenv(
    "RESUME_PATTERN", r"*[References|Resume].[docx|pdf]")
DRAFT_PATTERN = f"DRAFT-{RESUME_PATTERN}"


class ResumeDirectories:

    def __init__(self, root: Path) -> None:
        self.resume: Path = root / \
            os.getenv("RESUME_DIR", "resume")
        self.drafting: Path = self.resume / "drafting"
        self.docx: Path = self.resume / "docx"
        self.pdf: Path = self.resume / "pdf"
        self.published: Path = self.resume / "published"
        self.archive: Path = root / \
            os.getenv("ARCHIVE_DIR", "archive/resumes")

    def ensure_existence(self) -> None:
        dirs = []
        for name, value in self.__dict__.items():
            if isinstance(value, Path):
                if name == "archive":
                    value.mkdir(parents=True, exist_ok=True)
                    continue
                dirs.append({
                    "name": name, "exists": value.exists(), "path": value.absolute()
                })
        if not all([d['exists'] for d in dirs]):
            for m in [d for d in dirs if d['exists'] == False]:
                logger.error(
                    f"Missing directory '{m['name']}', path: '{m['path']}'")
            exit(1)


DIRS: ResumeDirectories = ResumeDirectories(ROOT_DIR)


class DateZone(Enum, tzinfo):

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> tzinfo:
        match name:
            case "LOCAL":
                local_tz_name = os.getenv("LOCAL_TIME_ZONE", None)
                if local_tz_name:
                    return ZoneInfo(local_tz_name)
                z = datetime.now().astimezone().tzinfo
                if z:
                    return z
                raise SystemError(
                    "Failed to get local timezone from system.")
            case "UTC":
                return pytz.utc
            case _:
                raise ValueError(
                    f"Invalid time zone name {name} for DateZone enum.")

    LOCAL = auto()
    UTC = auto()


class DateFormat(StrEnum):

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> str:
        _default_formats_str = r"%Y-%m-%d %H:%M:%S%T-%Z"
        env_key: str = f"{name}_DATE_FORMAT"

        default_format = _default_formats_str
        if name in ['SHORT', 'TIME']:
            default_format = _default_formats_str.split(
                " ")[0] if name == "SHORT" else _default_formats_str.split(" ")[1]

        env_format: str = os.getenv(env_key, default_format)
        return f"{env_format}"

    LONG = auto()
    ARCHIVE = auto()
    SHORT = auto()
    TIME = auto()


def get_datetime(zone: DateZone = DateZone.UTC) -> datetime:
    return datetime.now(zone)


def get_datestr(zone: DateZone = DateZone.UTC,
                format: DateFormat = DateFormat.LONG) -> str:
    now_datetime = get_datetime(zone=zone)
    return now_datetime.strftime(format=format.value)


get_utc_datestr = partial(get_datestr, zone=DateZone.UTC)
get_local_datestr = partial(get_datestr, zone=DateZone.LOCAL)


def archive_published_resume() -> None:
    files: list[Path] = []
    for item in DIRS.published.glob(RESUME_PATTERN):
        files.append(item)

    if len(files) == 0 or not files:
        raise FileNotFoundError(
            "No resume documents found in published folder.")

    utc_date_str = get_datetime().isoformat()
    archival_date_str = get_local_datestr(format=DateFormat.ARCHIVE)

    for f in files:
        a_path = DIRS.archive / f"{f.stem}{archival_date_str}{f.suffix}"
        f.copy(target=a_path, preserve_metadata=True)
        os.remove(f)


def main() -> None:
    pass
