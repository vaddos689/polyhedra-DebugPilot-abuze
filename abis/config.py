import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()

ABIS_DIR = os.path.join(ROOT_DIR, 'abis')

DEBUG_PILOT_ABI = os.path.join(ABIS_DIR, 'debugpilot.json')
BRIDGE_ABI = os.path.join(ABIS_DIR, 'bridge_abi.json')
BRIDGE_OPBNB = os.path.join(ABIS_DIR, 'bridge_opbnb.json')
OPBNB_CLAIM_NFT_ABI = os.path.join(ABIS_DIR, 'opbnb_claim_abi.json')
