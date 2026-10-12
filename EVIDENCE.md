# Evidence: Match on GenLayer StudioNet

Every row below was read back from the chain by `scripts/evidence.mjs`: the
sender, the status and the outcome come from the node's answer for each hash,
not from the deployment record. Every outcome on chain matches the record.

- **Contract:** [`0xcc9d9D05CB053d06d8736E312bA8D61E79534235`](https://explorer-studio.genlayer.com/address/0xcc9d9D05CB053d06d8736E312bA8D61E79534235)
- **Deploy transaction:** [`0xf9a4ddcb…661b`](https://explorer-studio.genlayer.com/tx/0xf9a4ddcb42260ce369fb01278a618b24d5284780a19b7f3e29bf49a4aea4661b)
- **Source sha256:** `4e02f3a9396b834404e3f61d8e77b21519295079360a0228fd3f47690241f652`
- **Transactions:** 12, from 6 different wallets
- **Generated:** 2026-10-12 03:11 UTC

## Wallets

Each wallet was made in memory for this run, and its key was never written
anywhere. Click an address to see every transaction it sent.

| Role | Address | Transactions sent |
|---|---|---|
| matcher | [`0xE28361d6a33a9Ab96b451De9D578B082C20bc8fD`](https://explorer-studio.genlayer.com/address/0xE28361d6a33a9Ab96b451De9D578B082C20bc8fD) | 3 |
| ann | [`0xbF0947704479c626794930Ed67C96c1a467c9a7D`](https://explorer-studio.genlayer.com/address/0xbF0947704479c626794930Ed67C96c1a467c9a7D) | 2 |
| ben | [`0x75d6726B8734B0f97d86F0147f1fAA6F087D67F5`](https://explorer-studio.genlayer.com/address/0x75d6726B8734B0f97d86F0147f1fAA6F087D67F5) | 2 |
| cal | [`0x4A504b15f58756be48F2234D0458f350bb11da10`](https://explorer-studio.genlayer.com/address/0x4A504b15f58756be48F2234D0458f350bb11da10) | 1 |
| dev | [`0x25Eb3096a4bf4d10DE929A35334f262FEDA1FB9e`](https://explorer-studio.genlayer.com/address/0x25Eb3096a4bf4d10DE929A35334f262FEDA1FB9e) | 1 |
| stranger | [`0x1a3dAB515A5A9C391544a1ED8ae0b6D51460BeAf`](https://explorer-studio.genlayer.com/address/0x1a3dAB515A5A9C391544a1ED8ae0b6D51460BeAf) | 3 |

## Transactions, in order

"refused" is a transaction the contract was meant to refuse: the committee
agreed on the refusal, and the sentence is the contract's own.

| # | Step | Sent by | Method | On chain | Outcome | Tx |
|---|---|---|---|---|---|---|
| 0 | deploy | matcher [`0xE283…c8fD`](https://explorer-studio.genlayer.com/address/0xE28361d6a33a9Ab96b451De9D578B082C20bc8fD) | `deploy` | FINALIZED · MAJORITY_AGREE | executed | [`0xf9a4ddcb…661b`](https://explorer-studio.genlayer.com/tx/0xf9a4ddcb42260ce369fb01278a618b24d5284780a19b7f3e29bf49a4aea4661b) |
| 1 | fund 0 opened: 0.6 GEN pool, 1:1, cap 0.2 | matcher [`0xE283…c8fD`](https://explorer-studio.genlayer.com/address/0xE28361d6a33a9Ab96b451De9D578B082C20bc8fD) | `open` | FINALIZED · MAJORITY_AGREE | executed | [`0x8bae89b8…2814`](https://explorer-studio.genlayer.com/tx/0x8bae89b855e8b4a608e95d1eadb2d38349e8fe2692658b3e71610e2558b82814) |
| 2 | the matcher gives to its own fund | matcher [`0xE283…c8fD`](https://explorer-studio.genlayer.com/address/0xE28361d6a33a9Ab96b451De9D578B082C20bc8fD) | `give` | FINALIZED · MAJORITY_AGREE | refused: the matcher cannot give to its own fund | [`0x32a3ef05…7c0a`](https://explorer-studio.genlayer.com/tx/0x32a3ef0550b17e0b73d4061c51db9a8375bc81169ed423728812f8a203e17c0a) |
| 3 | gift 0: Ann, 0.1 GEN to the reading club | ann [`0xbF09…9a7D`](https://explorer-studio.genlayer.com/address/0xbF0947704479c626794930Ed67C96c1a467c9a7D) | `give` | FINALIZED · MAJORITY_AGREE | executed | [`0xddd3587a…8ffe`](https://explorer-studio.genlayer.com/tx/0xddd3587ab7f823de8e9da93d92317be8a90df442922e790669e62f4b11ac8ffe) |
| 4 | gift 1: Ben, 0.25 GEN to the library | ben [`0x75d6…67F5`](https://explorer-studio.genlayer.com/address/0x75d6726B8734B0f97d86F0147f1fAA6F087D67F5) | `give` | FINALIZED · MAJORITY_AGREE | executed | [`0x6d833360…00be`](https://explorer-studio.genlayer.com/tx/0x6d83336083376965d4c8d8297f3c0c07c93948b9a97b22ea3be6ccaf4dd800be) |
| 5 | gift 2: Cal, 0.1 GEN to a football club | cal [`0x4A50…da10`](https://explorer-studio.genlayer.com/address/0x4A504b15f58756be48F2234D0458f350bb11da10) | `give` | FINALIZED · MAJORITY_AGREE | executed | [`0x93dd1e91…b419`](https://explorer-studio.genlayer.com/tx/0x93dd1e91777c7dca170a37a832597dc231c998e20fcfd76c49fa75f4191eb419) |
| 6 | gift 3: Dev, 0.05 GEN to a ward in Manchester | dev [`0x25Eb…FB9e`](https://explorer-studio.genlayer.com/address/0x25Eb3096a4bf4d10DE929A35334f262FEDA1FB9e) | `give` | FINALIZED · MAJORITY_AGREE | executed | [`0x550131ea…55f1`](https://explorer-studio.genlayer.com/tx/0x550131ea47a4ea4ae83053252d5ba440c0d4d4ff8fd4eb4f3967c82797de55f1) |
| 7 | Ann gives to herself | ann [`0xbF09…9a7D`](https://explorer-studio.genlayer.com/address/0xbF0947704479c626794930Ed67C96c1a467c9a7D) | `give` | FINALIZED · MAJORITY_AGREE | refused: a donor cannot give to itself | [`0x4eb9cadb…22e8`](https://explorer-studio.genlayer.com/tx/0x4eb9cadb24b045f754b3172f7760badba64e4886a74156075f784584ece822e8) |
| 8 | Ben gives to the reading club, already matched | ben [`0x75d6…67F5`](https://explorer-studio.genlayer.com/address/0x75d6726B8734B0f97d86F0147f1fAA6F087D67F5) | `give` | FINALIZED · MAJORITY_AGREE | refused: this fund already matched a gift to this recipient; give to it directly | [`0xf20a965b…defe`](https://explorer-studio.genlayer.com/tx/0xf20a965b28bf0a1cc56eef498a779a32f6b8efcedf83f9e8c159a3e6d9cedefe) |
| 9 | a close while gifts are open | stranger [`0x1a3d…BeAf`](https://explorer-studio.genlayer.com/address/0x1a3dAB515A5A9C391544a1ED8ae0b6D51460BeAf) | `close` | FINALIZED · MAJORITY_AGREE | refused: gifts are open until 2026-10-09T23:04:12Z | [`0x21418617…00d0`](https://explorer-studio.genlayer.com/tx/0x214186171d154977db0b33647cb8ef3289d5205a8592f276013fc6ba6f7400d0) |
| 10 | a gift after the window closed | stranger [`0x1a3d…BeAf`](https://explorer-studio.genlayer.com/address/0x1a3dAB515A5A9C391544a1ED8ae0b6D51460BeAf) | `give` | FINALIZED · MAJORITY_AGREE | refused: gifts closed at 2026-10-09T23:04:12Z; a gift after the window is never judged | [`0x181ed215…c830`](https://explorer-studio.genlayer.com/tx/0x181ed2155d3eea2783d70fbbc092b4e10e907bc42fff0c5ae207fa93b4dcc830) |
| 11 | fund 0 closed: the rest back to the matcher | stranger [`0x1a3d…BeAf`](https://explorer-studio.genlayer.com/address/0x1a3dAB515A5A9C391544a1ED8ae0b6D51460BeAf) | `close` | FINALIZED · MAJORITY_AGREE | executed | [`0xbfb4d1b6…76e9`](https://explorer-studio.genlayer.com/tx/0xbfb4d1b63991373e70e2d67f7634a9a5904070a7be268b723fa2a738630776e9) |
