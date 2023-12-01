from solcx import compile_standard, install_solc
import json
import os
from py_dotenv import read_dotenv
from web3 import Web3

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
read_dotenv(dotenv_path)

with open('./contracts/Simple_Storage.sol', "r") as file:
    simple_storage_file = file.read()

# Instalamos Solidity Version
install_solc("0.6.0")

# Compilar
compile_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "Simple_Storage.sol": {
            "content": simple_storage_file,
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": [
                    "abi",
                    "metadata",
                    "evm.bytecode",
                    "evm.bytecode.sourceMap",
                ]
            }
        }
    }
}, solc_version="0.6.0")

with open("./json/compile_sol_json.json", "w") as file:
    json.dump(compile_sol, file)

bytecode = compile_sol["contracts"]["Simple_Storage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

abi = json.loads(compile_sol["contracts"]["Simple_Storage.sol"]["SimpleStorage"]["metadata"])["output"]["abi"]

# Conexion a Ganache para hacer el despliegue
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_SERVER")))

chain_id = 1337
my_address = os.getenv("MY_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Nonce
nonce = w3.eth.get_transaction_count(my_address)

# Construir la transacción
transaction = SimpleStorage.constructor().build_transaction({
    "chainId": chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": my_address,
    "nonce": nonce
})

# Firmar la transacción
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Enviar la transacción
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Waiting for transaction...")

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Trabajar con contratos desplegados
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# CALL -> SIMULA UN LLAMADO PARA OBTENER UN VALOR
# Transact
print(simple_storage.functions.retrieve().call())

store_transaction = simple_storage.functions.store(15).build_transaction({
    "chainId": chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": my_address,
    "nonce": nonce + 1  # Incrementar el nonce para la nueva transacción
})

print("Modificando Valor")

signed_transaction = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)

t_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(t_hash)

print(simple_storage.functions.retrieve().call())
