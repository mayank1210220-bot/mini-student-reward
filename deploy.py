import time
import hashlib
import re
from stellar_sdk import Keypair, Network, TransactionBuilder
from stellar_sdk.soroban_server import SorobanServer
import requests
import urllib3
urllib3.disable_warnings()

print("Initializing deployment...")
kp = Keypair.random()
print(f"Deployer account: {kp.public_key}")
requests.get(f"https://friendbot.stellar.org/?addr={kp.public_key}", verify=False)

rpc = SorobanServer("https://soroban-testnet.stellar.org:443")
account = rpc.load_account(kp.public_key)

try:
    with open("target/wasm32v1-none/release/soroban_mini_reward_contract.wasm", "rb") as f:
        wasm_bytes = f.read()

    print("Uploading WASM...")
    tx1 = TransactionBuilder(account, Network.TESTNET_NETWORK_PASSPHRASE, base_fee=100000) \
        .append_upload_contract_wasm_op(wasm_bytes) \
        .set_timeout(30) \
        .build()

    sim1 = rpc.simulate_transaction(tx1)
    if not sim1 or getattr(sim1, 'error', None):
        print(f"Simulation failed: {sim1}")
        exit(1)

    tx1 = rpc.prepare_transaction(tx1, sim1)
    tx1.sign(kp)
    res1 = rpc.send_transaction(tx1)

    while True:
        st1 = rpc.get_transaction(res1.hash)
        if st1.status != "NOT_FOUND":
            break
        time.sleep(2)
        
    print(f"WASM upload: {st1.status}")

    wasm_id = hashlib.sha256(wasm_bytes).hexdigest()

    print("Instantiating contract...")
    account = rpc.load_account(kp.public_key)
    tx2 = TransactionBuilder(account, Network.TESTNET_NETWORK_PASSPHRASE, base_fee=100000) \
        .append_create_contract_op(wasm_id=wasm_id, address=kp.public_key) \
        .set_timeout(30) \
        .build()

    sim2 = rpc.simulate_transaction(tx2)
    tx2 = rpc.prepare_transaction(tx2, sim2)
    tx2.sign(kp)
    res2 = rpc.send_transaction(tx2)

    while True:
        st2 = rpc.get_transaction(res2.hash)
        if st2.status != "NOT_FOUND":
            break
        time.sleep(2)

    print(f"Contract instantiation: {st2.status}")

    match = re.search(r"C[A-Z0-9]{55}", str(sim2))
    if match:
        print(f"\n============================================\nSUCCESS! DEPLOYED CONTRACT ID:\n> {match.group(0)} <\n============================================\n")
        # WRITE TO APP.JS DIRECTLY
        with open("frontend/app.js", "r") as app_f:
            content = app_f.read()
        content = content.replace("PUT_YOUR_DEPLOYED_CONTRACT_ID_HERE", match.group(0))
        with open("frontend/app.js", "w") as app_f:
            app_f.write(content)
        print("Updated frontend/app.js automatically!")
    else:
        print("COULD NOT FIND ID IN SIM2:", sim2)
except Exception as e:
    import traceback
    traceback.print_exc()
