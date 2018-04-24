from enum import Enum
from typing import List

class ChargeType(Enum):
    PAYMENT = 1
    STANDARD_TRANSFER = 2
    CHARGE = 3

class ChargeStatus(Enum):
    COMPLETE = 1
    ISSUED = 2
    PENDING = 3

class Header(Enum):
    ID = 0
    DATE_TIME = 1
    TYPE = 2
    STATUS = 3
    NOTE = 4
    FROM = 5
    TO = 6
    AMT = 7
    FEE = 8
    FUND_SOURCE = 9
    DEST = 10

def process_csv(primary_user: str, csv_file: str) -> None:
    csv = _load_and_preprocess(csv_file)

def _load_and_preprocess(csv_file: str) -> List[str]:
    with open(csv_file) as f:
        data = f.read()

    data = data.split("\n")[1:-1]
    data = [d.split(",") for d in data]
    for i in range(len(data)):
        data_row = data[i]
        to_enum(data_row, Header.TYPE, ChargeType)
        to_enum(data_row, Header.STATUS, ChargeStatus)
        data_row[Header.AMT] = parse_dollar(data_row[Header.AMT.value])
        data_row[Header.FEE] = parse_dollar(data_row[Header.FEE.value])


def to_enum(row: List[str], header: Header, klass) -> None:  
    item = row[header.value]
    item = item.upper()
    item = item.replace(" ", "_")
    row[header.value] = klass[item]

def parse_dollar(dlr_str: str) -> float:
    pass


if __name__ == "__main__":
    process_csv("Vishal Kuo", "samples/download (1).csv")