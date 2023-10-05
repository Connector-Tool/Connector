input_poly = [
    {
        "event": "Transfer",
        "args": {
            "from": "0xb758B6576221a7504A7211307092C23D3eE191c9",
            "to": "0x81910675DbaF69deE0fD77570BFD07f8E436386A",
            "value": 112855947137612614726,
        }
    },
    {
        "event": "Approval",
        "args": {
            "owner": "0xb758B6576221a7504A7211307092C23D3eE191c9",
            "spender": "0x81910675DbaF69deE0fD77570BFD07f8E436386A",
            "value": 115792089237316195423570985008687907853269984665640564039121398728608095784048,
        }
    },
    {
        "event": "Approval",
        "args": {
            "owner": "0x81910675DbaF69deE0fD77570BFD07f8E436386A",
            "spender": "0x250e76987d838a75310c34bf422ea9f1AC4Cc906",
            "value": 0,
        }
    },
    {
        "event": "Approval",
        "args": {
            "owner": "0x81910675DbaF69deE0fD77570BFD07f8E436386A",
            "spender": "0x250e76987d838a75310c34bf422ea9f1AC4Cc906",
            "value": 112855947137612614726,
        }
    },
    {
        "event": "Approval",
        "args": {
            "from": "0x81910675DbaF69deE0fD77570BFD07f8E436386A",
            "to": "0x250e76987d838a75310c34bf422ea9f1AC4Cc906",
            "value": 112855947137612614726,
        }
    },
    {
        "event": "Approval",
        "args": {
            "owner": "0x81910675DbaF69deE0fD77570BFD07f8E436386A",
            "spender": "0x250e76987d838a75310c34bf422ea9f1AC4Cc906",
            "value": 0,
        }
    },
    {
        "event": "CrossChainEvent",
        "args": {
            "sender": "0xb758B6576221a7504A7211307092C23D3eE191c9",
            "txId": "0000000000000000000000000000000000000000000000000000000000010CC2",
            "proxyOrAssetContract": "0x250e76987d838a75310c34bf422ea9f1AC4Cc906",
            "toChainId": 6,
            "toContract": "2F7AC9436BA4B548F9582AF91CA1EF02CD2F1F03",
            "rawdata": "200000000000000000000000000000000000000000000000000000000000010CC2201C3A44703A99F1278496252B1B9847AF5D0476DE320250CEA55B1FB84996C83614250E76987D838A75310C34BF422EA9F1AC4CC9060600000000000000142F7AC9436BA4B548F9582AF91CA1EF02CD2F1F0306756E6C6F636B4A14E552FB52A4F19E44EF5A967632DBC320B082063914B758B6576221A7504A7211307092C23D3EE191C9468CA937FCDD301E060000000000000000000000000000000000000000000000",
        }
    },
    {
        "event": "LockEvent",
        "args": {
            "fromAssetHash": "0x9E32b13ce7f2E80A01932B42553652E053D6ed8e",
            "fromAddress": "0x81910675DbaF69deE0fD77570BFD07f8E436386A",
            "toChainId": 6,
            "toAssetHash": "E552FB52A4F19E44EF5A967632DBC320B0820639",
            "toAddress": "B758B6576221A7504A7211307092C23D3EE191C9",
            "amount": 112855947137612614726,
        }
    },
    {
        "event": "PolyWrapperLock",
        "args": {
            "fromAsset": "0x9E32b13ce7f2E80A01932B42553652E053D6ed8e",
            "sender": "0xb758B6576221a7504A7211307092C23D3eE191c9",
            "toChainId": 6,
            "toAddress": "B758B6576221A7504A7211307092C23D3EE191C9",
            "net": 112855947137612614726,
            "fee": 582308397918425,
            "id": 0
        }
    }
]

input_celer = [
    {
        "event": "Deposit",
        "args": {
            "dst": "0x5427FEFA711Eff984124bFBB1AB6fbf5E3DA1820",
            "wad": 110000000000000000,
        }
    },
    {
        "event": "Send",
        "args": {
            "transferId": "0x89d8051e597ab4178a863a5190407b98abfeff406aa8db90c59af76612e58f01",
            "sender": "0xE6265630324ba09143946D097F5a0A0099D32d2c",
            "receiver": "0xE6265630324ba09143946D097F5a0A0099D32d2c",
            "token": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "amount": 110000000000000000,
            "dstChainId": 137,
            "nonce": 1639586493904,
            "maxSlippage": 10533,
        }
    }
]

def PolyNetwork_keyExtractAndMap(input: list)->list:
    # Exist LockEvent event E and E.fromAddress = sender and
    # E.toAddress = receiver and E.fromAssetHash = assets and
    # E.toAssetHash = assetd and E.amount = amount and E.toChainId
    # = dstChainId
    results = []
    if any(item["event"] == "LockEvent" for item in input) == True:
        data_arr = [item for item in input if item["event"] == 'LockEvent']
        for data in data_arr:
            result = {
                "event": "Deposit",
                "args": {}
            }
            result["args"]["sender"] = data['args']['fromAddress']
            result["args"]["receiver"] = data['args']['toAddress']
            result["args"]["asset_s"] = data['args']['fromAssetHash']
            result["args"]["asset_d"] = data['args']['toAssetHash']
            result["args"]["amount"] = data['args']['amount']
            result["args"]["dstChainId"] = data['args']['toChainId']
            results.append(results)
    return results

def CelerNetwork_keyExtractAndMap(input:list)->list:
    # (Exist Send event E and E.sender = sender and E.receiver = receiver
    # and E.token = asset and E.amount = amount and dstChainId =
    # dstChainId) or (Exist Deposited event E and E.depositor = sender and
    # E.mintAcount = receiver and E.token = asset and E.amount = amount
    # and E.mintChainId = dstChainId) or (Exist LogNewTranserOut event
    # E and E.sender = sender and E.receiver = receiver and E.token = asset
    # and E.amount = amount and E.dstChainId = dstChainId)
    results = []
    

    if any(item["event"] == "Send" for item in input) == True:
        data_arr = [item for item in input if item["event"] == 'Send']
        for data in data_arr:
            result = {
                "event": "Deposit",
                "args": {}
            }
            result["args"]["sender"] = data['args']['sender']
            result["args"]["receiver"] = data['args']['receiver']
            result["args"]["asset"] = data['args']['token']
            result["args"]["amount"] = data['args']['amount']
            result["args"]["dstChainId"] = data['args']['dstChainId']
            results.append(result)

    elif any(item["event"] == "Deposited" for item in input) == True:
        data_arr = [item for item in input if item["event"] == 'Deposited']
        for data in data_arr:
            result = {
                "event": "Deposit",
                "args": {}
            }
            result["args"]["sender"] = data['args']['depositor']
            result["args"]["receiver"] = data['args']['mintAcount']
            result["args"]["asset"] = data['args']['token']
            result["args"]["amount"] = data['args']['amount']
            result["args"]["dstChainId"] = data['args']['mintChainId']
            results.append(result)

    elif any(item["event"] == "LogNewTranserOut" for item in input) == True:
        data_arr = [item for item in input if item["event"] == 'LogNewTranserOut']
        for data in data_arr:
            result = {
                "event": "Deposit",
                "args": {}
            }
            result["args"]["sender"] = data['args']['sender']
            result["args"]["receiver"] = data['args']['receiver']
            result["args"]["asset"] = data['args']['token']
            result["args"]["amount"] = data['args']['amount']
            result["args"]["dstChainId"] = data['args']['dstChainId'] 
            results.append(result)

    return results

def Multichain_keyExtractAndMap(input: list)->list:
#    (Exist LogSwapout event E and E.account = sender and E.bindaddr
#     = receiver and E.amount = amount) or (Exist LogAnySwapOut event
#     E and E.from = sender and E.to = receiver and E.token = asset and
#     E.amount = amount)
    
    results = []
    if any(item["event"] == "LogSwapout" for item in input) == True:
        data_arr = [item for item in input if item["event"] == 'LogSwapout']
        for data in data_arr:
            result = {
                "event": "Deposit",
                "args": {}
            }
            result["args"]["sender"] = data['args']['account']
            result["args"]["receiver"] = data['args']['bindaddr']
            result["args"]["amount"] = data['args']['amount']
            results.append(result)

    elif any(item["event"] == "LogAnySwapOut" for item in input) == True:
        data_arr = [item for item in input if item["event"] == 'LogAnySwapOut']
        for data in data_arr:
            result = {
                "event": "Deposit",
                "args": {}
            }
            result["args"]["sender"] = data['args']['from']
            result["args"]["receiver"] = data['args']['to']
            result["args"]["amount"] = data['args']['amount']
            results.append(result)

    return results

def keyExtractAndMap(input:dict, bridge:str)->dict:
    return eval(bridge+"_keyExtractAndMap")(input)

# key = keyExtractAndMap(input_celer, "CelerNetwork")
# print(key)