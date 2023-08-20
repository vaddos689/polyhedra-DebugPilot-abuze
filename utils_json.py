import json
from typing import Union, Optional
from data.data import DATA


def read_json(path: str, encoding: Optional[str] = None) -> list | dict:
    return json.load(open(path, encoding=encoding))


def get_chain_rpc(chain: str) -> str:
    return DATA[chain]['rpc']


def get_chain_scan_link(chain: str) -> str:
    return DATA[chain]['scan']


def get_chain_chain_id(chain: str) -> str:
    return DATA[chain]['chain_id']
