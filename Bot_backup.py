from web3 import Web3
import requests
import csv
import time
import pandas as pd
import os
from eth_account import Account
import json
import eth_abi
import os
from dotenv import load_dotenv
import warnings
from brownie import contracts,web3,accounts,DexExecutor
from eth_utils import to_bytes,to_checksum_address


warnings.filterwarnings('error')
FALLBACK_TOKEN_MAP = {
    "WETH": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
    "USDC": "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",
    "USDT": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
    "ARB": "0x912ce59144191c1204e64559fe8253a0e49e6548",
    "DAI": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
    "WBTC": "0x2f2a2543b76a4166549f7aaab1e5fcfffd7d52ea",
    "LINK": "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",
    "GMX": "0xfc5a1a6eb076a2c7a3d3d3f62cb6f2a53fae6abb",
    "MAGIC": "0x539bdE0d7Dbd336b79148AA742883198BBF60342",
    "RDNT": "0x0C4681e6C0235179ec3D4F4fc4DF3d14FDD96017",
    "GRAIL": "0x3DaFBA57A67622b8C9bA0e45e0E5377835e8C1A5",
    "SPA": "0x5575552988A3A80504bBAeb1311674fE0DBD0B4C",
    "VST": "0x64343594ab9b56e99087bfa6f2335db24c2d1f17",
    "VELA": "0x088cd8f5ef3652623c22d48b1605dcfe860cd704",
    "PLS": "0x51318b7d00db7acc4026c88c3952b66278b6a67f",
    "JONES": "0x10393c20975cf177a3513071bc110f7962cd67da",
    "DODO": "0xe4cD47a4f42A178b5fC6a127B0952bBf55196b4B",
    "LUSD": "0x93b346b6bc2548da6a1e7d98e9a421b42541425b",
    "RELAY": "0x08d1e4dbd6b8bb1f9dd660c34c3fe63a1ec733fc",
    "BRC": "0x0c880f6761f1af8d9aa9c466984b80dab9a8c9e8", 
    "BCOIN": "0xbbcb0356bb9e6b3faa5cbf9e5f36185d53403ac9",
    "BCSPX": "0x1e2c4fb7ede391d116e6b41cd0608260e8801d59",
    "BERNA": "0x0f76d32cdccdcbd602a55af23eaf58fd1ee17245",
    "BERNX": "0x3f95aa88ddbb7d9d484aa3d482bf0a80009c52c9",
    "BGME": "0x7212088a11b4d8f6fc90fbb3dfe793b45dd72323",
    "BC3M": "0x2f123cf3f37ce3328cc9b5b8415f9ec5109b45e7",
    "BHIGH": "0x20c64dee8fda5269a78f2d5bdba861ca1d83df7a",
    "BIB01": "0xca30c93b02514f86d5c86a6e375e3a330b435fb5",
    "BIBTA": "0x52d134c6db5889fad3542a09eaf7aa90c0fdf9e4",
    "BMSFT": "0x374a457967ba24fd3ae66294cab08244185574b0",
    "BMSTR": "0xac28c9178acc8ba4a11a29e013a3a2627086e422",
    "BNIU": "0x2f11eeee0bf21e7661a22dbbbb9068f4ad191b86",
    "BCSBGC3": "0xd8b95b1987741849ca7e71e976aeb535fd2e55a2",
    "BTSLA": "0x14a5f2872396802c3cc8942a39ab3e4118ee5038",
    "BZPR1": "0xade6057fcafa57d6d51ffa341c64ce4814995995",
    "BADGER": "0xbfa641051ba0a0ad1b0acf549a89536a0d76472e",
    "BAL": "0x040d1edc9569d4bab2d15287dc5a4f10f56a56b8",
    "DLP": "0x32df62dc3aed2cd6224193052ce665dc18165841",
    "BALN": "0xac7952d30850c9d214b0f44cbe213781b4dacf05",
    "BOND": "0x0d81e50bc677fa67341c44d7eaa9228dee64a4e1",
    "BSKT": "0xa3210cd727fe6daf8386af5623ba51a367e46263",
    "GFLY": "0x872bad41cfc8ba731f811fea8b2d0b9fd6369585",
    "PET": "0x43c25f828390de5a3648864eb485cc523e039e67",
    "BEAN": "0xbea0005b8599265d41256905a9b3073d397812e4",
    "BIC": "0xb1c3960aeeaf4c255a877da04b06487bba698386",
    "BETS": "0x94025780a1ab58868d9b2dbbb775f44b32e8e6e5",
    "BDG": "0x56264286b18903889d03de41cf6acfab1fe1defc",
    "BICO": "0xa68ec98d7ca870cf1dd0b00ebbb7c4bf60a8e74d",
    "BAMA": "0x5d4974f8543bc78d43fd1044ecfdb9d85482aa21",
    "BOGE": "0xfd2fb8de10ec41ddd898a8c7fa70d8fc100834c4",
    "BTRM": "0x221c5799209132766a01c4cbed0d28600d282b41",
    "FTW": "0x306fd3e7b169aa4ee19412323e1a5995b8c1a1f4",
    "BDT": "0x21ccbc5e7f353ec43b2f5b1fb12c3e9d89d30dca",
    "BLKC": "0x8626264b6a1b4e920905efd381002aba52ea0eea",
    "BUIDL": "0xa6525ae43edcd03dc08e775774dcabd3bb925872",
    "BLADE": "0xe8b201be5357c07f0aa58693f98fb048323777f9",
    "BLOK": "0x9dce8e754913d928eb39bc4fc3cf047e364f7f2c",
    "MYRC": "0x3ed03e95dd894235090b3d4a49e0c3239edce59e",
    "BNVDA": "0xa34c5e0abe843e10461e2c9586ea03e55dbcc495",
    "BOB": "0xb0b195aefa3650a6908f15cdac7d92f8a5791b0b",
    "$BONER": "0xf9ca0ec182a94f6231df9b14bd147ef7fb9fa17c",
    "BONK": "0x09199d9a5f4448d0848e4395d065e1ad9c4a1f74",
    "BONSAI": "0x79ead7a012d97ed8deece279f9bc39e264d7eef9",
    "BONZAI": "0x0a84edf70f30325151631ce7a61307d1f4d619a3",
    "$BOO": "0x28514bd097d5f9ecea778cc7a4ca4bac5fedb0b6",
    "BOOP": "0x13a7dedb7169a17be92b0e3c7c2315b46f4772b3",
    "GORPLES": "0x0002bcdaf53f4889bf2f43a3252d7c03fe1b80bc",
    "TIA.N": "0xd56734d7f9979dd94fae3d67c7e928234e71cd4c",
    "TUSD": "0x4d15a3a2286d883af0aa1b3f21367843fac63e07",
    "USDE": "0x5d3a1ff2b6bab83b63cd9ad0787074081a52ef34",
    "AXL-WSTETH": "0x9cfb13e6c11054ac9fcb92ba89644f30775436e4",
    "BRIX": "0xf65247b6ed3e7fdbac313959b3f62475fbb5f8e4",
    "BRUH": "0xb5b5b428e4de365f809ced8271d202449e5c2f72",
    "AIBB": "0xb9af4762c039d63e30039f1712dfab77026408c7",
    "BUMP": "0xfb930d1a28990820c98144201637c99bea8cb91c",
    "BYTE": "0x847503fbf003ce8b005546aa3c03b80b7c2f9771",
    "CADAI": "0x4debfb9ed639144cf1e401674af361ffffcefb58",
    "CADC": "0x2b28e826b55e399f4d4699b85f68666ac51e6f70",
    "GRAIL": "0x3d9907f9a368ad0a51be60f7da3b97cf940982d8",
    "CTSI": "0x319f865b287fcc10b30d8ce6144e8b6d1b476999",
    "CARV": "0xc08cd26474722ce93f4d0c34d16201461c10aa8c",
    "CATMOUSE": "0xafa5676a6ef790f08290dd4a45e0ec2a5cc5cdab",
    "CELR": "0x3a8b787f78d775aecfeea15706d4221b40f345ab",
    "CELO": "0x4e51ac49bc5e2d87e0ef713e9e5ab2d71ef4f336",
    "CGETH.HASHKEY": "0x0ce45dd53affbb011884ef1866e0738f58ab7969",
    "XCHNG": "0x51c601dc278eb2cfea8e52c4caa35b3d6a9a2c26",
    "LINK": "0xf97f4df75117a78c1a5a0dbb814af92458539fb4",
    "CDT": "0x0cbd6fadcf8096cc9a43d90b45f65826102e3ece",
    "CR": "0xe018c227bc84e44c96391d3067fab5a9a46b7e62",
    "CHR": "0x15b2fb8f08e4ac1ce019eadae02ee92aedf06851",
    "CHUNKS": "0x894a3abb764a0ef5da69c62336ac3c15b88bf106",
    "CLBTC": "0x1792865d493fe4dfdd504010d3c0f6da11e8046d",
    "CLUTCH": "0xf4acde4d938844751f34659c67056f7e69dbe85a",
    "CTOK": "0xa586b3b80d7e3e8d439e25fbc16bc5bcee3e2c85",
    "CBPAY": "0xd6cf874e24a9f5f43075142101a6b13735cdd424",
    "CBBTC": "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf",
    "CBETH": "0x1debd73e752beaf79865fd6446b0c970eae7732f",
    "COLLAB": "0xf18c263ec50cc211ef3f172228549b6618f10613",
    "COLX": "0xe5cca68b9e1d5575b7e3062fa34b0c725b003a69",
    "COMP": "0x354a6da3fcde098f8389cad84b0182725c6c91de",
    "CNFI": "0x6f5401c53e2769c858665621d22ddbf53d8d27c5",
    "NEXT": "0x58b9cb810a68a7f3e1e4f8cb45d1b9b3c79705e8",
    "TANGO": "0xc760f9782f8cea5b06d862574464729537159966",
    "OOOI": "0xd7b675cd5c84a13d1d0f84509345530f6421b57c",
    "CX": "0x000000000000012def132e61759048be5b5c6033",
    "COW": "0xcb8b5cd20bdcaea9a010ac1f8d835824f5c87a04",
    "CREAM": "0xf4d48ce3ee1ac3651998971541badbb9a14d7234",
    "CBL": "0xd6b3d81868770083307840f513a3491960b95cb6",
    "MNLT": "0x0a1694716de67c98f61942b2cab7df7fe659c87a",
    "CAW": "0x16f1967565aad72dd77588a332ce445e7cef752b",
    "CRVUSD": "0x498bf2b1e120fed3ad3d42ea2165e9b73f99c1e5",
    "CIP": "0xd7a892f28dedc74e6b7b33f93be08abfc394a360",
    "CU": "0x89c49a3fa372920ac23ce757a029e6936c0b8e02",
    "CRYSTAL": "0xd07d35368e04a839dee335e213302b21ef14bb4a",
    "CRV": "0x11cdb42b0eb46d95f990bedd4695a6e3fa034978",
    "2CRV": "0x7f90122bf0700f9e7e1f688fe926940e8839f353",
    "CVPAD": "0x259b0f9494b3f02c652fa11417b94cb700f1f7d8",
    "CYG": "0x05eaea39f69b24f8f2da13af2d8ee0853889f2a8",
    "D2": "0xed7f000ee335b8199b004cca1c6f36d188cf6cb8",
    "DACKIE": "0x47c337bd5b9344a6f3d6f58c474d9d8cd419d8ca",
    "DAO": "0xcaa38bcc8fb3077975bbe217acfaa449e6596a84",
    "RING": "0x9e523234d36973f9e38642886197d023c88e307e",
    "DUSD": "0x8ec1877698acf262fe8ad8a295ad94d6ea258988",
    "SDUSD": "0x5a691001bf7065a17e150681f5bfbd7bc45a668e",
    "DEURO": "0x5e85faf503621830ca857a5f38b982e0cc57d537",
    "MONEY": "0x69420f9e38a4e60a62224c489be4bf7a94402496",
    "DEGEN": "0x9f07f8a82cb1af1466252e505b7b7ddee103bc91",
    "DERI": "0x21e60ee73f17ac0a411ae5d690f908c3ed66fe12",
    "DRV": "0x77b7787a09818502305c95d68a2571f090abb135",
    "ALOT": "0x9d5a383581882750ce27f84c72f017b378edb736",
    "GDEX": "0x92a212d9f5eef0b262ac7d84aea64a0d0758b94f",
    "KIT": "0x9134283afaf6e1b45689ec0b0c82ff2b232bcb30",
    "DF": "0xae6aab43c4f3e0cea4ab83752c278f8debaba689",
    "DFX": "0x27f485b62c4a7e635f561a87560adf5090239e93",
    "DGW": "0x9cce9ae579142e372a8959285e3a5a2e211904f7",
    "DHT": "0x8038f3c971414fd1fc220ba727f2d4a0fc98cb65",
    "DRC": "0x2b089381f53525451fe5115f23e9d2cc92d7ff1d",
    "AAPL.D": "0xce38e140fc3982a6bcebc37b040913ef2cd6c5a7",
    "ADBE.D": "0x289594b223ab31832726eb99871fa99adac583e5",
    "AMC.D": "0x28bf1c9ee2eb746a2d61a0bec97a344028171d6c",
    "AMD.D": "0xd8f728adb72a46ae2c92234ae8870d04907786c5",
    "AMZN.D": "0x8240affe697cde618ad05c3c8963f5bfe152650b",
    "ARKB.D": "0x3619ca1e96c629f7d71c1b03dc0ee56479356228",
    "ARKK.D": "0x1a4fd0e749c86eeb6f80d1047d6c25432c703d48",
    "ARKX.D": "0x10ddf4850c43de1bcab504f53becdcd66a53d5c4",
    "ARM.D": "0x67bad479f77488f0f427584e267e66086a7da43a",
    "AVGO.D": "0x7c5fed5e0f8d05748cc12ffe1ca400b07de0f983",
    "AZN.D": "0x44966bf47a494b36dfb407afb334a9226cdf90bc",
    "BA.D": "0x6b8ba11c987795fe11fe23f15e1f3d0f3e4e0bba",
    "BAC.D": "0x23f318840a200fa488627849a369a138f66b3577",
    "BITB.D": "0x769ff50fd49900a6c53b2af049eacb83dad52bdf",
    "BLK.D": "0xf2f26eee8b40447f664f20ad3513e894153fe09e",
    "BOXX.D": "0xcd3246f6173217dbecf63ffab83d477b266679da",
    "BRK.A.D": "0x9da913f4dca9b210a232d588113047685a4ed4b1",
    "BRRR.D": "0x2b7c643b42409f352b936bf07e0538ba20979bff",
    "BTCO.D": "0x2824efe5cedb3bc8730e412981997dac7c7640c2",
    "BTCW.D": "0xc52915fe75dc8db9fb6306f43aaef1344e0837ab",
    "CAT.D": "0xe649980d1b911756f217e4b61de76a7d2a3b108a",
    "CCL.D": "0xa81323f79c4f3887e18cc2702b31635a56ec606e",
    "COIN.D": "0x46b979440ac257151ee5a5bc9597b76386907fa1",
    "COST.D": "0xd17aff8fcf7698aabfb5f8be90aa2692774fa810",
    "CSCO.D": "0x337842843512192b798a5592053ce8e2245651f8",
    "CVX.D": "0x0e929101c4fa7c91eaa64d7216161ba3eee387fe",
    "DAL.D": "0xcc603c6626408fbfe2c1fea3565acb5d10c85274",
    "DEFI.D": "0xdd92f0723a7318e684a88532cac2421e3cc9968e",
    "DIS.D": "0x3c9f23db4ddc5655f7be636358d319a3de1ff0c4",
    "EEM.D": "0x5b041a4e76b08c5afc1e0b9a789cbfab5ebec993",
    "ERO.D": "0x071e1fd14fbacb2b856867043eb12ace1ee3cb52",
    "ETHE.D": "0x4cb894d1a5fc353ec18ba50cb087b88f6f73121f",
    "EZBC.D": "0xa6f344abc6e2501b2b303fcbba99cd89f136b5fb",
    "F.D": "0x7af89514dadd0a39b5e87f013b0f3fd2ed591c88",
    "FBTC.D": "0x026fdf3024953cb2e8982bc11c67d336f37a5044",
    "GBTC.D": "0xb1284f6b3e487e3f773e9ad40f337c3b3cda5c69",
    "GLD.D": "0xbe8e3f4d5bd6ee0175359982cc91dafa3cf72502",
    "GME.D": "0xb415998a7bb6f11dc589e0eb20adf586ba32f12a",
    "GOOGL.D": "0x8e50d11a54cff859b202b7fe5225353be0646410",
    "HODL.D": "0x0c59f6b96d3cac58240429c7659ec107f8b1efa7",
    "HOOD.D": "0x0753d920a5e37b0bf2114a7b4a71d46f66ce4b30",
    "HUT.D": "0x808167ea744e02c6fec3f56636d19f3448b72981",
    "HYMB.D": "0xef5713f65e32332b604e1096e68a6d78a0e927cf",
    "IAU.D": "0x39bce681d72720f80424914800a78c63fdfaf645",
    "IBIT.D": "0xc1ba16afdcb3a41242944c9faaccd9fb6f2b428c",
    "ITA.D": "0xf1f313acc8c65dc2e7eebeb166c7c30be634eb38",
    "JNJ.D": "0x50e2b96f958133cbda56d1a62d156e812fe97828",
    "JPM.D": "0xe15602ceeb794feb4163b049fe82a1f8432781b2",
    "KO.D": "0x42ba3ac0c2d9b611623e1e48f51757606a105d9e",
    "LMT.D": "0x893ff58cd1e34eac0c8ce4fa92b30adee4e14986",
    "MARA.D": "0xc0ce7221db1508529752339c3bd5dcf01fa1b0ca",
    "MCD.D": "0x0c29891dc5060618c779e2a45fbe4808aa5ae6ad",
    "MELI.D": "0x41c9954ff544c2376385afc15d11d9bcfac777ab",
    "META.D": "0x519062155b0591627c8a0c0958110a8c5639dca6",
    "MSFT.D": "0x77308f8b63a99b24b262d930e0218ed2f49f8475",
    "MSTR.D": "0xdf7a6ce3b9087251f5859f42ca79ce34f4a88460",
    "NFLX.D": "0x3ad63b3c0ea6d7a093ff98fde040baddc389ecdc",
    "NLY.D": "0x14297be295ab922458277be046e89f73382bdf8e",
    "NVDA.D": "0x4dafffddea93ddf1e0e7b61e844331455053ce5c",
    "PALL.D": "0x7a2abf0543674ba1bb618b1e88118e8a4fefab48",
    "PFE.D": "0xf1f18f765f118c3598cc54dcac1d0e12066263fe",
    "PG.D": "0xb90e1ee5f4194388e71c11dc2a4eea16da391ce4",
    "PHO.D": "0xad6a646c1b262586ef3a8b6c6304e7c9218ecac4",
    "PLD.D": "0x118346c2bb9d24412ed58c53bf9bb6f61a20d7ec",
    "PPLT.D": "0x3774a2e7c66bc9371424c3edc67503cadd7c882b",
    "PYPL.D": "0x5b6424769823e82a1829b0a8bcaf501bffd90d25",
    "QQQ.D": "0xad84746c961bc3142b0aefeb0a51a2880bbe4795",
    "RBLX.D": "0x6468cd2aa21a87b4e52d89b8dd123fbb5db101ed",
    "RDDT.D": "0x97ec5dada8262bd922bffd54a93f5a11efe0b136",
    "RIOT.D": "0x0b5ac0d7dcf6964609a12af4f6c6f3c257070193",
    "RKLB.D": "0xe3b82cfbfeda73dc6870d76090061bc3c97d25ac",
    "SBUX.D": "0x4b72de2da8be112cad87773b47537cf550676ffa",
    "SIVR.D": "0x1adedd1fe0237858d151ec043b218fe6d2b9bf2a",
    "SLX.D": "0x0a2919147b871a0fc90f04944e31fad56d9af666",
    "SNOW.D": "0x1ae31840d492993a58baf558180b5ee83ce2f8ce",
    "SONY.D": "0x5644fe2f365397a0313ee323da3ead314405c09a",
    "SOXL.D": "0x9fe6002c876972d8d84124ec25000a6fa14c88ec",
    "SPSK.D": "0xa213072a726062aca3c07839b7e531f101740c5c",
    "SPTE.D": "0x1795eeacbf98f08e7ee5af0a8913d5a54c24bb40",
    "SPUS.D": "0x2594a6392832b341b76b60e8b00f42094e30b1b3",
    "SPWO.D": "0xccf43c38fe53c633425e14f6aba50a98e5ab1408",
    "SPY.D": "0xf4bd09b048248876e39fcf2e0cdf1aee1240a9d2",
    "SQ.D": "0xd883bcf80b2b085fa40cc3e2416b4ab1cbca649e",
    "TJX.D": "0x50f7b76a0b888e5d7196f1a472d2e567d425c761",
    "TQQQ.D": "0x63ad78a6e2db3322d16943fc65e71a0010571521",
    "TSLA.D": "0x36d37b6cbca364cf1d843eff8c2f6824491bcf81",
    "UFO.D": "0x3f29fda039ee80f7d30fa5eb4e3b40691329f020",
    "USD+": "0xfc90518d5136585ba45e34ed5e1d108bd3950cfa",
    "USFR.D": "0x9c46e1b70d447b770dbfc8d450543a431af6df3a",
    "USHY.D": "0xeb32d26ab45b5c6cfe6c924adf00f8d5953dadf3",
    "V.D": "0x96e1951c8fcecc43e7366261f7e342a06047da8e",
    "VWO.D": "0x1bed98b79f8a5e32031b0d735022fc006db47d37",
    "VXX.D": "0x40914f6007da3fcee3c8a6db211b5797848f8882",
    "WALRF.D": "0x92b81204dd07b14ff8664092897ab660ce3ab323",
    "WEAT.D": "0xc20770116f2821d550574c2b9ce1b4baa7012377",
    "WOOD.D": "0x13f950ee286a5be0254065d4b66420fc0e57adfc",
    "XOM.D": "0x315a2dca4b1b633d3a707c71d96243534c02f7c4",
    "YUM.D": "0xeb0d1360a14c3b162f2974daa5d218e0c1090146",
    "DZHV": "0x3419875b4d3bca7f3fdda2db7a476a79fd31b4fe",
    "IBTC": "0x050c24dbf1eec17babe5fc585f06116a259cc77a",
    "DODO": "0x69eb4fa4a2fbd498c257c57ea8b7655a2559a581",
    "DOLA": "0x6a7661795c374c0bfc635934efaddff3a7ee23b6",
    "DOMDOM": "0x635d0e13f98e107cf6c5cdfbf52c19843f87e76a",
    "DONUT": "0xf42e2b8bc2af8b110b65be98db1321b1ab8d44f5",
    "DPX": "0x6c2c06790b3e3e3c38e12ee22f8183b37a13ee55",
    "RDPX": "0x32eb7902d4134bf98a28b963d26de779af92a212",
    "$DORAB": "0x6612ce012ba5574a2ecea3a825c1ddf641f78623",
    "DMT": "0x8b0e6f19ee57089f7649a455d89d7bc6314d04e8",
    "EKO": "0x370f01c998b583e7cc9a7ee79be8ed0bb27345e7",
    "ECLIP": "0x93ca0d85837ff83158cd14d65b169cdb223b1921",
    "EMC": "0xdfb8be6f8c87f74295a87de951974362cedcfa30",
    "EDG": "0x4e0da40b9063dc48364c1c0ffb4ae9d091fc2270",
    "EGP": "0x7e7a7c916c19a45769f6bdaf91087f93c6c12f78",
    "EUSD": "0x12275dcb9048680c4be40942ea4d92c74c63b844",
    "ELM": "0xeeac5e75216571773c0064b3b591a86253791db6",
    "EMP": "0x772598e9e62155d7fdfe65fdf01eb5a53a8465be",
    "ENO": "0x2b41806cbf1ffb3d9e31a9ece6b738bf9d6f645f",
    "EQU": "0x87aaffdf26c6885f6010219208d5b161ec7609c0",
    "EQB": "0xbfbcfe8873fe28dfa25f1099282b088d52bbad9c",
    "EPENDLE": "0xd4848211b699503c772aa1bc7d33b433c4242ac3",
    "NOX": "0xf34450d1f23902657cffb2636153677be7d38750",
    "ELG": "0x89d59a38eb2a91df58a709bb249bf1d13ad11037",
    "ESPRF": "0xfc675adfdd721064ba923d07a8a238a9e52d8ace",
    "EMAX": "0x123389c2f0e9194d9ba98c21e63c375b67614108",
    "ETH+": "0xd4939d69b31fbe981ed6904a3af43ee1dc777aab",
    "ETHFI": "0x7189fb5b6504bbff6a852b13b7b82a3c118fdc27",
    "ETHFAI": "0x67c31056358b8977ea95a3a899dd380d4bced706",
    "ERN": "0xa334884bf6b0a066d553d19e507315e839409e62",
    "EUROE": "0xcf985aba4647a432e60efceeb8054bbd64244305",
    "EUTBL": "0xcbeb19549054cc0a6257a77736fc78c367216ce7",
    "EVA": "0x45d9831d8751b2325f3dbf48db748723726e1c8c",
    "EYWA": "0x7a10f506e4c7658e6ad15fdf0443d450b7fa80d7",
    "FCTR": "0x6dd963c510c2d2f09d5eddb48ede45fed063eb36",
    "FTN": "0x1045971c168b5294acbc8727a4f1c9e1af99f6d0",
    "BOMB": "0x74ccbe53f77b08632ce0cb91d3a545bf6b8e0979",
    "FRM": "0x9f6abbf0ba6b5bfa27f4deb6597cc6ec20573fda",
    "CHF24": "0xd41f1f0cf89fd239ca4c1f8e8ada46345c86b0a4",
    "EUR24": "0x2c5d06f591d0d8cd43ac232c2b654475a142c7da",
    "USD24": "0xbe00f3db78688d9704bcb4e0a827aea3a9cc0d62",
    "FNXAI": "0x3088e120b220e67a2e092f5da8cdf02ea0170f6a",
    "FLAME": "0x4a7779abed707a9c7deadbbef5c15f3e52370a99",
    "FFM": "0x3269a3c00ab86c753856fd135d97b87facb0d848",
    "AI": "0x8d7c2588c365b9e98ea464b63dbccdf13ecd9809",
    "FLY": "0x000f1720a263f96532d1ac2bb9cdc12b72c6f386",
    "FUSDC": "0x4cfa50b7ce747e2d61724fcac57f24b748ff2b2a",
    "FLUX": "0xf80d589b3dbe130c270a69f1a69d050f268786df",
    "FORE": "0xcbe94d75ec713b7ead84f55620dc3174beeb1cfe",
    "BENJI": "0xb9e4765bce2609bc1949592059b17ea72fee6c6a",
    "FRAX": "0x17fc002b466eec40dae837fc4be5c67993ddbd6f",
    "FRXETH": "0x178412e79c25968a32e89b11f63b33f733770c2a",
    "FPI": "0x1b01514a2b3cdef16fd3c680a818a0ab97da8a09",
    "FPIS": "0x3405e88af759992937b84e58f2fe691ef0eea320",
    "FRAX": "0x9d2f299715d94d8a7e6f5eaa8e654e8c74a988a7",
    "FU": "0x130096af9163b185cae4a833f856760199fc6ceb",
    "FUSE": "0x6b021b3f68491974be6d4009fee61a4e3c708fd6",
    "FST": "0x488cc08935458403a0458e45e20c0159c8ab2c92",
    "GNS": "0x18c11fd286c5ec11c3b683caa813b77f5163a122",
    "GUSDC": "0xd3443ee1e91af28e5fb858fbd0d72a63ba8046e0",
    "GALAXIS": "0xa5312c3e42a82d459162b2a3bd7ffc4f9099b911",
    "G3": "0xc24a365a870821eb83fd216c9596edd89479d8d7",
    "G7": "0xf18e4466f26b4ca55bbab890b314a54976e45b17",
    "GMB": "0xa0c8d91b6dce36f6deeadf716ab02bc539d9bebf",
    "GSWIFT": "0x580e933d90091b9ce380740e3a4a39c67eb85b4c",
    "GS": "0xb08d8becab1bf76a9ce3d2d5fa946f65ec1d3e83",
    "SEED": "0x86f65121804d2cdbef79f9f072d4e0c2eebabc08",
    "LASAGNA": "0x344c796cc2474e4b779d0e81765afb91d7741a42",
    "GMAC": "0xdc8b6b6beab4d5034ae91b7a1cf7d05a41f0d239",
    "INETH": "0x5a7a183b6b44dc4ec2e3d2ef43f98c5152b1d76d",
    "GENSX": "0xf29fdf6b7bdffb025d7e6dfdf344992d2d16e249",
    "$GENE": "0x59a729658e9245b0cf1f8cb9fb37945d2b06ea27",
    "GHO": "0x7dff72693f6a4149b17e7c6314655f6a9f7c8b33",
    "USDGLO": "0x4f604735c1cf31399c6e711d5962b2b3e0225ad3",
    "GMX": "0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a",
    "GNOME": "0x42069d11a2cc72388a2e06210921e839cfbd3280",
    "GNO": "0xa0b862f60edef4452f25b4160f177db44deb6cf1",
    "GOA": "0x8c6bd546fb8b53fe371654a0e54d7a5bd484b319",
    "GOLD": "0x8b5e4c9a188b1a187f2d1e80b1c2fb17fa2922e1",
    "GOOD": "0x17176a9868f321411b15ccb9b934cf95597e89c4",
    "GOB": "0xa2f9ecf83a48b86265ff5fd36cdbaaa1f349916c",
    "GOHM": "0x8d9ba570d6cb60c7e3e0f31343efe75ab8e65fb1",
    "GOVI": "0x07e49d5de43dda6162fa28d24d5935c151875283",
    "GRAI": "0x894134a25a5fac1c2c26f1d8fbf05111a3cb9487",
    "GRAIN": "0x80bb30d62a16e1f2084deae84dc293531c3ac3a1",
    "@G": "0x440017a1b021006d556d7fc06a54c32e42eb745b",
    "GRIX": "0x812f2d5ff6088ed7a655567dbcdf0d42cf07ca38",
    "GUARD": "0xbcf339df10d78f2b44aa760ead0f715a7a7d7269",
    "GUBERTO": "0x4727a7d2022e99ee5c298513b730307f458f9b40",
    "GYEN": "0x589d35656641d6ab57a545f08cf473ecd9b6d5f7",
    "GYD": "0xca5d8f8a8d49439357d3cf46ca2e720702f132b8",
    "HOL": "0x65c101e95d7dd475c7966330fa1a803205ff92ab",
    "FOREX": "0xdb298285fe4c5410b05390ca80e8fbe9de1f259b",
    "HARAMBE": "0x255f1b39172f65dc6406b8bee8b08155c45fe1b6",
    "HAT": "0x4d22e37eb4d71d1acc5f4889a65936d2a44a2f15",
    "HEGIC": "0x431402e8b9de9aa016c743880e04e517074d8cec",
    "HHI": "0x65d51305e969ff19d96954c4a75d8e9fde86ce07",
    "HERMES": "0x45940000009600102a1c002f0097c4a500fa00ab",
    "ANON": "0x79bbf4508b1391af3a0f4b30bb5fc4aa9ab0e07c",
    "HIP": "0xa0995d43901551601060447f9abf93ebc277cec2",
    
}

load_dotenv()  # loads from .env by default
contract_address_real = []
contract_address_fork = []
contract_abi=[]
def bundle_flash_loan(
    token_in,#token to borrow
    token_out,#token to trade
    buy_dex,# lowest price dex 
    sell_dex,#highest price dex
    amount,
    contract_address,
    abi_path=contract_abi
):
    # === Alchemy Arbitrum Setup ===
    ALCHEMY_KEY = os.getenv("alchemy_api_key")
    ALCHEMY_URL = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"
    PRIVATE_KEY = os.getenv("WALLET_KEY")
    
    web3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
    account = Account.from_key(PRIVATE_KEY)
    ACCOUNT_ADDRESS = account.address
    
    #amount_wei=Web3.to_wei(amount, 'mwei')

    # === Load Contract ===
    contract_address = Web3.to_checksum_address(contract_address)
    with open(abi_path) as f:
        contract_abi = json.load(f)
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # === Encode Parameters for initiateArbitrage ===
    params = eth_abi.encode(
        ['address', 'address', 'address', 'address', 'uint256'],
        [
            Web3.to_checksum_address(buy_dex),
            Web3.to_checksum_address(sell_dex),
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out),
            0  # minReturn = 0
        ]
    )

    # === Build Transaction ===
    tx = contract.functions.initiateArbitrage(
        Web3.to_checksum_address(token_in),
        amount_wei,
        params
    ).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        'gasPrice': web3.eth.gas_price,
        'chainId': 42161  # Arbitrum One
    })

    # === Estimate Gas and Send ===
    tx['gas'] = web3.eth.estimate_gas(tx)
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print(f"Flashloan TX sent: {web3.to_hex(tx_hash)}")
    return web3.to_hex(tx_hash)

ALCHEMY_KEY = os.getenv("alchemy_api_key")
ALCHEMY_URL = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"
PRIVATE_KEY = os.getenv("WALLET_KEY")
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

# Transaction hash (replace with your actual transaction hash)
tx_hash = None

# Check status of a transaction
def check_for_pending_tx(tx_hash):
    if tx_hash is None:
        return 0
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if receipt and receipt.status in (0, 1):
            return 0  # success or failure
    except Exception as e:
        return e
    return 1  # pending





# Arbiscan API Key
arbiscan_api_key = 'NG1EFT9ARUX3D2USIBA3BHNR5ZBRE8WFQJ' #change to .env


ALCHEMY_KEY = os.getenv("alchemy_api_key")
ALCHEMY_URL = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"
PRIVATE_KEY = os.getenv("WALLET_KEY")
web3= Web3(Web3.HTTPProvider(ALCHEMY_URL))


# Basic ABIs for Uniswap V2 and V3
METHOD_FORMATS = {
    "v2": {
        "method": "swapExactTokensForTokens",
        "args_format": [
            "uint256",        # amountIn
            "uint256",        # amountOutMin
            "address[]",      # path
            "address",        # recipient
            "uint256"         # deadline
        ]
    },
    "dodo": {
        "method": "dodoSwapV2TokenToToken",
        "args_format": [
            "address",        # tokenIn
            "address",        # tokenOut
            "uint256",        # amountIn
            "uint256",        # minReturnAmount
            "address[]",      # mixPairs (empty for default)
            "uint256"         # deadline
        ]
    },
    "uniswapV3": {
        "method": "exactInputSingle",
        "args_format": {
            "tokenIn": "address",
            "tokenOut": "address",
            "fee": "uint24",
            "recipient": "address",
            "deadline": "uint256",
            "amountIn": "uint256",
            "amountOutMinimum": "uint256",
            "sqrtPriceLimitX96": "uint160"
        }
    }
}


DEX_LIST = [
    ["SushiSwap", Web3.toChecksumAddress("0x1b02da8cb0d097eb8d57a175b88c7d8b47997506"), "v2"],
    ["Camelot", Web3.toChecksumAddress("0xc873fecbd354f5a56e00e710b90ef4201db2448d"), "v2"],
    ["TraderJoe", Web3.toChecksumAddress("0xb4315eaf84bf6b1bdfcf3f9b5e6f5f8f1a42f66e"), "v2"],
    ["Chronos", Web3.toChecksumAddress("0x46d3ecbf6e7410aef4b032054f1c409a0efc9b71"), "v2"],
    ["ZyberSwap", Web3.toChecksumAddress("0x5bd7cc970f1b9fbc4730dc84c74e6f2f1e3fca3c"), "v2"],
    ["Ramses", Web3.toChecksumAddress("0xaaa479483c2d2f0649474ea42e64dfd947ec849c"), "v2"],
    ["SolidLizard", Web3.toChecksumAddress("0xa4d7aC61bCfb2457aEfB3cDaF9D39d22f932e62d"), "v2"],
    ["KyberSwap", Web3.toChecksumAddress("0x1c87257f5e8609940bc751a07bb085bb7f8cdbe6"), "v2"],
    ["DODO", Web3.toChecksumAddress("0xa222e6a71d1a1dd5f279805fbe38d5329c1d0e70"), "dodo"],
    ["UniswapV3", Web3.toChecksumAddress("0xe592427a0aece92de3edee1f18e0157c05861564"), "uniswapV3"]
]


# Global ABI cache
cache_dex_abi = {}

# ERC20 minimal ABI
ERC20_ABI = [
    {"constant": True, "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
]

# --- DEX Routers (Arbitrum) ---
DEX_ROUTERS = {
    "SushiSwap":     "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",
    "Camelot":       "0xc873fecbd354f5a56e00e710b90ef4201db2448d",
    "TraderJoe":     "0xb4315eaf84bf6b1bdfcf3f9b5e6f5f8f1a42f66e",
    "Chronos":       "0x46d3ecbf6e7410aef4b032054f1c409a0efc9b71",
    "ZyberSwap":     "0x5bd7cc970f1b9fbc4730dc84c74e6f2f1e3fca3c",
    "Ramses":        "0xaaa479483c2d2f0649474ea42e64dfd947ec849c",
    "SolidLizard":   "0xa4d7aC61bCfb2457aEfB3cDaF9D39d22f932e62d",
    "KyberSwap":     "0x1c87257f5e8609940bc751a07bb085bb7f8cdbe6",
    "DODO":          "0xa222e6a71d1a1dd5f279805fbe38d5329c1d0e70",
}

# Uniswap V3 Quoter and fee tiers
UNIV3_QUOTER = Web3.to_checksum_address("0x61fFE014bA17989E743c5F6cB21bF9697530B21e")
UNIV3_FEE_TIERS = [100, 500, 3000, 10000]


# --- Token resolution helpers ---
def resolve_token(symbol: str):
    address = FALLBACK_TOKEN_MAP.get(symbol.upper())
    if not address:
        print(f"Token '{symbol}' not found.")
        return None
    try:
        return Web3.to_checksum_address(address)
    except Exception:
        return None

def get_token_info(address):
    try:
        address = Web3.to_checksum_address(address)
        token = web3.eth.contract(address=address, abi=ERC20_ABI)
        symbol = token.functions.symbol().call()
        decimals = token.functions.decimals().call()
        return {"address": address, "symbol": symbol, "decimals": decimals}
    except:
        return None


# --- Quoting functions with ABI cache ---
def get_v2_quote(router_addr, token_in, token_out, amount_in):
    try:
        if router_addr not in cache_dex_abi:
            contract = Contract.from_explorer(router_addr)
            cache_dex_abi[router_addr] = contract.abi
        router = Contract.from_abi("V2Router", router_addr, cache_dex_abi[router_addr])
        amounts = router.getAmountsOut.call(amount_in, [token_in, token_out])
        return amounts[-1]
    except:
        return 0

def get_v3_quote(token_in, token_out, amount_in, fee_tiers, quoter_addr):
    best_quote = 0
    best_fee = None
    try:
        if quoter_addr not in cache_dex_abi:
            contract = Contract.from_explorer(quoter_addr)
            cache_dex_abi[quoter_addr] = contract.abi
        quoter = Contract.from_abi("V3Quoter", quoter_addr, cache_dex_abi[quoter_addr])

        for fee in fee_tiers:
            try:
                quote = quoter.quoteExactInputSingle.call(token_in, token_out, fee, amount_in, 0)
                if quote > best_quote:
                    best_quote = quote
                    best_fee = fee
            except:
                continue
    except:
        return 0, None
    return best_quote, best_fee


# --- DEX price comparison ---
def compare_prices_across_dex(token_in, token_out, amount_in, dex_routers, quoter, fee_tiers):
    results = []

    for name, addr in dex_routers.items():
        addr = Web3.to_checksum_address(addr)
        quote = get_v2_quote(addr, token_in, token_out, amount_in)
        results.append({
            "dex": name,
            "price_out": quote,
            "address": addr,
            "type": "v2",
            "fee": None
        })

    v3_quote, v3_fee = get_v3_quote(token_in, token_out, amount_in, fee_tiers, quoter)
    results.append({
        "dex": "UniswapV3",
        "price_out": v3_quote,
        "address": quoter,
        "type": "v3",
        "fee": v3_fee
    })

    sorted_results = sorted(results, key=lambda x: x["price_out"], reverse=True)
    return {
        "best": sorted_results[0],
        "min": sorted_results[-1],
        "all": results
    }


# --- Human-readable quote function ---
def understand_price_gotten(token_in_symbol, token_out_symbol, amount, dex_routers, quoter, fee_tiers):
    token_in = resolve_token(token_in_symbol)
    token_out = resolve_token(token_out_symbol)
    if not token_in or not token_out:
        print("Could not resolve tokens.")
        return None

    token_in_info = get_token_info(token_in)
    token_out_info = get_token_info(token_out)
    if not token_in_info or not token_out_info:
        print("Could not fetch token metadata.")
        return None

    amount_in = int(amount * (10 ** token_in_info["decimals"]))
    result = compare_prices_across_dex(token_in, token_out, amount_in, dex_routers, quoter, fee_tiers)

    best = result["best"]
    worst = result["min"]

    return {
        "input_amount": amount,
        "token_in": token_in_info["symbol"],
        "token_out": token_out_info["symbol"],
        "best_dex": best["dex"],
        "best_price": best["price_out"] / (10 ** token_out_info["decimals"]),
        "best_fee": best["fee"],
        "worst_dex": worst["dex"],
        "worst_price": worst["price_out"] / (10 ** token_out_info["decimals"]),
        "worst_fee": worst["fee"],
    }



def get_ammount_to_profit(token_in_symbol, token_out_symbol, amount_in,DEX_ROUTERS,UNIV3_QUOTER,UNIV3_FEE_TIERS):
    compare = understand_price_gotten(token_in_symbol, token_out_symbol, amount_in,DEX_ROUTERS,UNIV3_QUOTER,UNIV3_FEE_TIERS)
    if not compare:
        return None
    print(compare)

    disc = compare["best_price"] - compare["worst_price"]
    if 0.0005 < disc <= 0.0009:
        return 1000000
    elif 0.001 < disc <= 0.009:
        return 1000000
    elif 0.005 < disc <= 0.009:
        return 100000
    elif 0.01 < disc <= 0.09:
        return 100000
    elif 1 < disc <= 9:
        return 1000
    elif  disc >= 9 :
        return 100
    
    return None



def build_swap_tx(router_addr, method_name, args):
    router = Contract.from_explorer(router_addr)
    method = getattr(router, method_name)
    calldata = method.encode_input(*args)
    return calldata
    
from brownie import accounts, Contract
from eth_abi import encode_abi



def estimate_gas_for_arbitrage(contract_address, abi, token_in, amount, buy_dex, sell_dex, token_out, min_return, bribe_token, bribe_swap_data):
    account = accounts[0]
    contract = Contract.from_abi("FlashArbitrage", contract_address, abi)

    params = encode_abi(
        ["address", "address", "address", "address", "uint256", "address", "bytes"],
        [buy_dex, sell_dex, token_in, token_out, min_return, bribe_token, bribe_swap_data]
    )

    gas_estimate = contract.initiateArbitrage.estimate_gas(
        token_in,
        amount,
        params,
        {"from": account}
    )

    print(f"Estimated gas: {gas_estimate}")
    return gas_estimate



def simulate_trade(token_in_symbol, token_out_symbol, amount_in,DEX_ROUTERS,UNIV3_QUOTER,UNIV3_FEE_TIERS,token_in,token_out):
    amount = get_ammount_to_profit(token_in_symbol, token_out_symbol, amount_in,DEX_ROUTERS,UNIV3_QUOTER,UNIV3_FEE_TIERS)
    if not amount:
        return None
    print(amount)

    result = understand_price_gotten(token_in_symbol, token_out_symbol, amount_in,DEX_ROUTERS,UNIV3_QUOTER,UNIV3_FEE_TIERS)
    if not result:
        return None
    print(result)

    disc = result["best_price"] - result["worst_price"]
    if 0.0005 < disc:
        Amount_init= amount
        final_amount= amount + disc
        Gas = estimate_gas_for_arbitrage(contract_address,abi, token_in_, amount, buy_dex, sell_dex, token_out,0,token_in, bribe_swap_data)
        if disc > 
        print('opportunity')
        return {
            "amount": 1000000,
            "best_dex_address": result["best_dex_address"],
            "worst_dex_address": result["worst_dex_address"],
            "price" : result["worst_price"]
        }
    elif 0.0001 < disc <= 0.0009:
       # print('oppurtunity')
        return {
            "amount": 1000000,
            "best_dex_address": result["best_dex_address"],
            "worst_dex_address": result["worst_dex_address"],
            "price" :result["worst_price"] 
        }
    elif 0.001 < disc <= 0.09:
        #print('opp')
        return {
            "amount": 100000,
            "best_dex_address": result["best_dex_address"],
            "worst_dex_address": result["worst_dex_address"],
            "price" :result["worst_price"]
        }
    elif 0.1 < disc <= 0.9:
        #print('opp')
        return {
            "amount": 10000,
            "best_dex_address": result["best_dex_address"],
            "worst_dex_address": result["worst_dex_address"],
            "price":result["worst_price"]
        }
    elif 1 < disc <= 9:
        #print('opp')
        return {
            "amount": 1000,
            "best_dex_address": result["best_dex_address"],
            "worst_dex_address": result["worst_dex_address"],
            "price" :result["worst_price"]
        }
    elif  disc >= 9 :
        #print('opp')
        return {
            "amount": 10,
            "best_dex_address": result["best_dex_address"],
            "worst_dex_address": result["worst_dex_address"],
            "price" :result["worst_price"]
       }

    return None

def arbitrage_bot(contract_address):
    index= 0
    tx_hash= 0
    symbols = list(FALLBACK_TOKEN_MAP.keys())
    for i in range(len(symbols)):
        token0 = symbols[i]
        token1 = "USDC"
        trade = simulate_trade(token0,token1)
        status = check_for_pending_tx(tx_hash)
        if trade and status ==0 and i == index:
            tx_hash = bundle_flash_loan(
                resolve_token(token1),
                resolve_token(token0),
                trade["worst_dex_address"],
                trade["best_dex_address"],
                trade["amount"]*trade["price"],
                contract_address
                ) 
            index = (i + 1) % len(symbols)
            break
        else:
            continue 

while True:
    try:
        arbitrage_bot(contract_address)
    except Exception as e:
        continue 
    except warnings as W:
        continue 
    
