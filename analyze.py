import csv
from enum import Enum
from typing import Any, List

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
    data = _load_and_preprocess(csv_file)
    total = 0
    for row in data:
        total += _process_row(row, primary_user)

    print(f"NET TRANSACTIONS: {round(total, 2)}")


def _process_row(row: List[Any], primary_user: str) -> float:
    # -ve is money out, +ve is money in
    if row[Header.TYPE.value] == ChargeType.STANDARD_TRANSFER:
        return 0

    if row[Header.STATUS.value] != ChargeStatus.COMPLETE:
        return 0

    dlr_amt = row[Header.AMT.value]
    fees = row[Header.FEE.value]
    if fees:
        dlr_amt -= fees
    
    return dlr_amt


def _load_and_preprocess(csv_file: str) -> List[str]:
    with open(csv_file) as f:
        data = list(csv.reader(f))[1:]

    for i in range(len(data)):
        data_row = data[i]
        _to_enum(data_row, Header.TYPE, ChargeType)
        _to_enum(data_row, Header.STATUS, ChargeStatus)
        _parse_dollar(data_row, Header.AMT)
        _parse_dollar(data_row, Header.FEE)

    return data


def _to_enum(row: List[str], header: Header, klass) -> None:
    item = row[header.value]
    item = item.upper()
    item = item.replace(" ", "_")
    row[header.value] = klass[item]


def _parse_dollar(row: List[str], header: Header) -> float:
    dlr_str = row[header.value]
    if not dlr_str:
        return 0
    dlr_amt = float(dlr_str.split("$")[1])
    row[header.value] = dlr_amt if dlr_str.startswith("+") else dlr_amt * -1


if __name__ == "__main__":
    process_csv("Vishal Kuo", "samples/download (1).csv")