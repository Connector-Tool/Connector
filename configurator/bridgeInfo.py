import pandas as pd

from config import Config
from utils.loader import read_data


def get_address_list(name:str, mainnet:str, output:list) ->list:
    addList = read_data(Config().ADDRESSLIST_DIR, name + ".csv")
    addList = addList[addList['srcnet'] == mainnet]
    result = pd.DataFrame(addList, columns=['address'])
    for item in output:
        result = pd.concat([result, pd.DataFrame(addList, columns=[item])], axis = 1)
    return result.to_dict(orient='records')


def get_chainID(name:str, chainID:int) ->str:
    chainId = read_data(Config().CHAINID_DIR, name)
    goal = chainId[chainId["chain_id"] == chainID]
    result = pd.DataFrame(goal, columns=['name'])
    return result.iat[0,0]


# 存款事件声明
def get_deposit_event(name: str, mainnet: str) -> list:
    eventList = read_data(Config().KNOWLEDGE_DIR['event'], name + ".csv")
    eventList = eventList[eventList['action'] == 'Deposit']
    eventList = eventList[eventList['example_tx_hash'].str.startswith(mainnet)]
    result = pd.DataFrame(eventList, columns=['event_name', 'arguments'])
    return result


# 存款函数声明（备用）
def get_deposit_func(name:str, mainnet:str) -> list:
    eventList = read_data(Config().KNOWLEDGE_DIR['func'], name + ".csv")
    eventList = eventList[eventList['action'] == 'Deposit']
    eventList = eventList[eventList['example_tx_hash'].str.startswith(mainnet)]
    result = pd.DataFrame(eventList, columns=['func_name', 'arguments'])
    return result


# 取款函数声明
def get_withdraw_event(name:str, mainnet:str) -> list:
    eventList = read_data(Config().KNOWLEDGE_DIR['event'], name + ".csv")
    eventList = eventList[eventList['action'] == 'Withdraw']
    eventList = eventList[eventList['example_tx_hash'].str.startswith(mainnet)]
    result = pd.DataFrame(eventList, columns=['event_name', 'arguments'])
    return result


# 取款事件声明
def get_withdraw_func(name:str, mainnet:str) -> list:
    eventList = read_data(Config().KNOWLEDGE_DIR['func'], name + ".csv")
    eventList = eventList[eventList['action'] == 'Withdraw']
    eventList = eventList[eventList['example_tx_hash'].str.startswith(mainnet)]
    result = pd.DataFrame(eventList, columns=['func_name', 'arguments'])
    return result