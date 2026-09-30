#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory
import ots
ROOT=Path(__file__).resolve().parents[1]
with TemporaryDirectory() as temp:
    for extension in ['ttf','woff2']:
        source=ROOT/f'fonts/TalynBrush-Regular.{extension}'
        result=ots.sanitize(str(source),str(Path(temp)/f'{extension}-sanitized.ttf'),check=True,capture_output=True)
        print(source.name+': '+result.stdout.decode().strip())
        if result.stderr: print(result.stderr.decode().strip())
