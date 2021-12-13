#!/usr/bin/env python3
import argparse
from typing import Dict, Tuple
import requests
from requests import adapters

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

_retry_strategy = Retry(
     total=3,
     status_forcelist=[429, 500, 502, 503, 504],
     # backoff factor plugs into the following {backoff factor} * (2 ** ({number of total retries} - 1))
     # means 0.5 1 2 4 8 16... as coded
     backoff_factor=1,
)

def _post_webhook(url: str, contents: Dict) -> None:
    requests.post(url=url, headers={
                  'Content-Type': 'application/json'}, json=contents)


def _slack_notify(message: str, webhook: str) -> None:
    payload = {'blocks': [
        {'type': 'section', 'text': {'type': 'mrkdwn', 'text': message}}]}
    _post_webhook(webhook, payload)


def _discord_notify(message: str, webhook: str) -> None:
    payload = {'content': message}
    _post_webhook(webhook, payload)


def _handle_rpc(connection_string: str, action: str, resp_params: str) -> str:
    adapter= HTTPAdapter(max_retries=_retry_strategy)
    http = requests.Session()
    http.mount('http://', adapter)
    http.mount('https://', adapter)
    url = f"http://{connection_string}"
    data = {"action": action}
    r = http.post(url, json=data, timeout=1)
    resp = r.json()
    ret = resp[resp_params]
    return ret


def _in_sync(connection_string: str) -> Tuple[bool, str, str]:
    block_count = _handle_rpc(connection_string, "block_count", "cemented")
    telemetry_count = _handle_rpc(
        connection_string, "telemetry", "cemented_count")
    count_delta = int(telemetry_count) - int(block_count)
    if (block_count > telemetry_count) and count_delta / float(telemetry_count) > 0.01:
        synced = False
    else:
        synced = True
    return synced, block_count, telemetry_count


def _out_of_sync(address: str, block_count: str, telemetry_count) -> str:
    return f"*ALERT*: Block count on the nano node at {address} " + \
        f"is more than 0.01% behind the median network values. " + \
        f"Local nano node block count: {block_count}, " + \
        f"Median network block count: {telemetry_count}. " + \
        f"Investigation and possible node restart is recommended."


def _timed_out(address: str) -> str:
    return f"*ALERT*: Local RPC calls to the nano node at {address} " + \
        f"timed out. Investigation is recommended."


def main(connect: str, slack: str, discord: str, nickname: str) -> None:
    if nickname != "":
        address = nickname
    else:
        address = connect.split(":")[0]
    try:
        in_sync, block_count, telemetry_count = _in_sync(connect)
        if not in_sync:
            print(_out_of_sync(
                address, block_count, telemetry_count))
            if slack != '':
                _slack_notify(
                    _out_of_sync(
                        address, block_count, telemetry_count),
                    slack)
            if discord != '':
                _discord_notify(
                    _out_of_sync(
                        address, block_count, telemetry_count),
                    discord)
    except (requests.Timeout, requests.ConnectionError):
        print(_timed_out(address))
        if slack != '':
            _slack_notify(
                _timed_out(address),
                slack)
        if discord != '':
            _discord_notify(
                _timed_out(address),
                discord)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='nmonit.py',
                                     description="""
    Simple Nano Node Monitoring Tool with optional slack and discord webhook notifications
    """)
    parser.add_argument('--connection_string', type=str,
                        default="localhost:7075", help='RPC connection of node ex: localhost:7075')
    parser.add_argument('--slack_webhook', dest='slack', type=str, default='',
                        help='Slack Websocket url to send to')
    parser.add_argument('--discord_webhook', dest='discord', type=str, default='',
                        help='Discord Webhook to send to')
    parser.add_argument('--nickname', type=str, default='',
                        help='endpoint nickname')
    args = parser.parse_args()
    main(args.connection_string, args.slack,
         args.discord, args.nickname)
