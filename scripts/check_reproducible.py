#!/usr/bin/env python3
from pathlib import Path
import hashlib
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
paths=sorted((ROOT/'fonts').glob('*'))+sorted((ROOT/'sources/svg').glob('*.svg'))+[ROOT/'sources/features.fea']
def snapshot():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=snapshot()
subprocess.run([sys.executable,str(ROOT/'scripts/build.py')],cwd=ROOT,check=True)
after=snapshot()
changed=[p for p in before if before[p]!=after[p]]
if changed:raise SystemExit('Non-reproducible outputs: '+', '.join(changed))
print(f'Reproducibility verified for {len(paths)} outputs.')
