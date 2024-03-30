import requests
import sys
import os
import time
from datetime import datetime
import numpy as np
# Para gráficos ASCII, você pode usar a biblioteca 'asciichartpy' (não é exatamente igual, mas similar)
import asciichartpy as asciichart


# Supondo que você tenha as variáveis de ambiente configuradas
rpc_url = os.getenv("RPC_URL")
wallet_address = os.getenv("WALLET")
auth_token = os.getenv("AUTH_TOKEN")

iterations = 0
second_history = []
minute_history = []
programs_ids = ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"]

def main():
    global iterations, second_history, minute_history
    iterations += 1
    wallet = {}
    for p in programs_ids:
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_token
        }
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet_address,
                {"programId": p},
                {"encoding": "jsonParsed"},
            ],
        }

        token_accounts_response = requests.post(rpc_url, json=body, headers=headers)
        token_accounts_json = token_accounts_response.json()

        for item in token_accounts_json['result']['value']:
            balance = item['account']['data']['parsed']['info']['tokenAmount']['uiAmount']
            mint = item['account']['data']['parsed']['info']['mint']
            if balance > 0:
                wallet[mint] = balance

        jupiter_url = f"https://price.jup.ag/v4/price?ids={','.join(wallet.keys())}"
        jupiter_response = requests.get(jupiter_url)
        jupiter_json = jupiter_response.json()

        wallet_balance = 0
        values = {}
        usd_to_brl_rate = 5  # Exemplo de taxa de conversão

        for token, balance in wallet.items():
            if token in jupiter_json['data']:
                price = jupiter_json['data'][token]['price'] * usd_to_brl_rate
                mint_symbol = jupiter_json['data'][token]['mintSymbol']
                value = balance * price
                wallet_balance += value
                values[mint_symbol] = value

    os.system('clear')
    print("Wallet Tracker")
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('\n')
    print("Last 5 minutes:")
    if second_history:
        if second_history[0] <= second_history[-1]:
            print(asciichart.plot(second_history, {'height': 10, 'colors': ["\033[92m"]}))
        else:
            print(asciichart.plot(second_history, {'height': 10, 'colors': ["\033[91m"]}))

    print("\nLast hour:")
    if minute_history:
        minute_data = minute_history + [second_history[-1]] if second_history else minute_history
        print(asciichart.plot(minute_data, {'height': 10}))

    second_history.append(wallet_balance)
    if iterations % 60 == 1:
        sorted_history = sorted(second_history)
        median_price = sorted_history[len(sorted_history) // 2]
        minute_history.append(median_price)

    if len(second_history) > 60:
        second_history.pop(0)
    if len(minute_history) > 60:
        minute_history.pop(0)

    # Exibir posições e balanço total em BRL
    for position, value in sorted(values.items(), key=lambda item: item[1], reverse=True):
        print(f"{position}\t{value:,.2f} BRL")

    print(f"Total balance: {wallet_balance:,.2f} BRL")


# Executa a função principal imediatamente e depois a cada 15 minutos
if __name__ == "__main__":
    main()
    while True:
        time.sleep(5)
        main()
