import json
from utils import shell, log
from config import GlobalConfig

# get config singleton
config = GlobalConfig.get()


def parse_artillery_output(report_file: str) -> bool:
    report = json.load(report_file)
    import pprint

    pprint(report)
