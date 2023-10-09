# Connector



## 🔰 Install

Before using `Connector` for cross-chain transaction tracking, please make sure that the relevant py library is installed in the virtual environment. Specifically, enter the following `pip` command at the end point of the virtual environment:


```
pip install -r requirements
```

## 🙌 How to use

`Connector` consists of several modules, specifically:

- `extractor`: For crawling blockchain data.
- `configurator`: For extracting key transaction information.
- `trained_model`: For training deposit transaction recognition models.
- `core`: For tracking deposit-withdrawal transaction pairs.
- `experiment`: For verifying model effects.
- `utils`: For storing some auxiliary code.


## 🎁 Datasets

The data folder of `Connector` is divided into four parts:

1️⃣ FirstPhrase
> Contains full transaction dataset.
- `ETH` addresses related to Celer cBridge: `Celer.csv`
- `ETH` transactions related to Celer cBridge addresses: `Celer_ETH.csv`
- `ETH` addresses related to Multichain: `Multi.csv`
- `ETH` transactions related to Multichain addresses: `Multi_ETH.csv`
- `ETH` addresses related to PolyNetwork: `Poly.csv`
- `ETH` transactions related to PolyNetwork addresses: `Poly_ETH.csv`


2️⃣ Model
> Contains model data related to deposit transaction recognition.
- Normalized mappings related to function variables: `normalization_map.csv`


3️⃣ Token
> Contains decimal place information for tokens on `ETH`, `BSC`, `Polygon`.
- Data related to ERC20 decimals for `ETH`: `ERC20.csv`
- Data related to ERC20 decimals for `BSC`: `BERC20.csv`
- Data related to ERC20 decimals for `Polygon`: `PERC20.csv`

4️⃣ Validation
> Contains real label data sets related to three bridges and three chains.

- Cross-chain transaction pair label: `label.csv`
- Source chain deposit transaction sample: `sample.json`
- Source chain deposit transaction input field: `input.csv`