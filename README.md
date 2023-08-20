# Информация
_Бот для проверки баланса в testnet bnb, минта панд, бриджа bnb в opbnb и бриджа панд [DebugPilot](https://zkbridge.com/gallery/pandra_debugpilot)_  
* Поддерживает многопоточнось
## Установка
установка библиотек
```bash
pip install -r requirements.txt
```
внесите свои приватные ключи от кошельков с балансом tbnb в private_keys.txt
## Usage
для запуска введите в консоль
```bash
python main.py
```
### Результат работы чекера баланса хранится а файле tbnb_balance.txt
### Результат работы минтера панд хранится по пути core/wallets_with_debugpilot.txt
### Результат работы бриджера храниться в файле wallets_with_opbnb_pandra.txt
