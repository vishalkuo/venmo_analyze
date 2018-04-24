import csv
from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List
import json

import click

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

class TransactionData(Enum):
    NET_AMT = 0
    GROUP_BY_FRIENDS = 1
    GROUP_BY_DATE = 2

@click.group()
def cli():
    pass

@cli.command()
@click.argument("report")
def analyze(report: str) -> None:
    """Analyzes a CSV Venmo statement and outputs relevant transaction data"""
    data = _load_and_preprocess(report)
    data_dict = {
        TransactionData.NET_AMT.name: 0,
        TransactionData.GROUP_BY_FRIENDS.name: defaultdict(float),
        TransactionData.GROUP_BY_DATE.name: defaultdict(float),
    }
    for row in data:
        _process_row(row, data_dict)

    print(json.dumps(data_dict, indent=4))


def _process_row(row: List[Any], data_dict: Dict[str, float]) -> None:
    # -ve is money out, +ve is money in
    if row[Header.TYPE.value] == ChargeType.STANDARD_TRANSFER:
        return 0

    if row[Header.STATUS.value] != ChargeStatus.COMPLETE:
        return 0

    dlr_amt = row[Header.AMT.value]
    fees = row[Header.FEE.value]
    if fees:
        dlr_amt -= fees

    friend_dict = data_dict[TransactionData.GROUP_BY_FRIENDS.name]
    if row[Header.TYPE.value] == ChargeType.CHARGE or dlr_amt < 0:
        friend_dict[row[Header.TO.value]] += dlr_amt
    else:
        friend_dict[row[Header.FROM.value]] += dlr_amt
    
    data_dict[TransactionData.NET_AMT.name] += dlr_amt


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
    dlr_amt = round(float(dlr_str.split("$")[1]), 2)
    row[header.value] = dlr_amt if dlr_str.startswith("+") else dlr_amt * -1


if __name__ == "__main__":
    cli()