from solcx import compile_standard , install_solc
import json
import os
from py_dotenv import read_dotenv
from web3 import Web3 

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
read_dotenv(dotenv_path)

with open('./contracts/Simple_Storage.sol' , "r") as file:
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
}, 
solc_version="0.6.0"
)


with open("./json/compile_sol_json.json", "w") as file:
    json.dump(compile_sol, file)


bytecode = compile_sol["contracts"]["Simple_Storage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]


abi = json.loads(compile_sol["contracts"]["Simple_Storage.sol"]["SimpleStorage"]["metadata"])["output"]["abi"]

# Conexion a garnache para hacer el despliege

w3 = Web3(Web3.HTTPProvider("HTTP://172.27.32.1:7545"))

chain_id = 1337
my_address = os.getenv("MY_ADDRESS")
private_key =  os.getenv("PRIVATE_KEY")

SimpkeStorage = w3.eth.contract(abi = abi, bytecode = bytecode);


# Nonce
nonce = w3.eth.get_transaction_count(my_address)

# Construir la transaccion
transaction = SimpkeStorage.constructor().build_transaction({
    "chainId":chain_id,
    "gasPrice":w3.eth.gas_price,
    "from":my_address,
    "nonce":nonce
})

#firmar la transaccion

signed_txn = w3.eth.account.sign_transaction(transaction , private_key=private_key )


#Enviar la transaccion
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Waiting for transaction...")

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(tx_receipt.contractAddress  )

