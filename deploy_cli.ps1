$stellarPath = "C:\Program Files (x86)\Stellar CLI\stellar.exe"
$wasmPath = "target\wasm32v1-none\release\soroban_mini_reward_contract.wasm"
$source = "admin"
$network = "testnet"
$passphrase = "Test SDF Network ; September 2015"

& $stellarPath contract deploy `
  --wasm $wasmPath `
  --source $source `
  --network $network `
  --network-passphrase $passphrase `
  --ignore-checks
