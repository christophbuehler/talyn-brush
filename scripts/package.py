#!/usr/bin/env python3
"""Create a deterministic, licensed font package and a static specimen site."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[1]
VERSION='v0.3.0'

def package():
    build=ROOT/'build';build.mkdir(exist_ok=True)
    files=['fonts/TalynBrush-Regular.ttf','fonts/TalynBrush-Regular.woff2','fonts/manifest.json',
           'OFL.txt','FONTLOG.txt','README.md','docs/OFL-FAQ.txt','docs/DESIGN.md','docs/PROVENANCE.md',
           'specimen/cyrillic.png','specimen/preview.png','specimen/words.png','specimen/german.png']
    target=build/f'TalynBrush-{VERSION}.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for rel in sorted(files):
            info=zipfile.ZipInfo('TalynBrush-'+VERSION+'/'+rel,(2026,10,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            archive.writestr(info,(ROOT/rel).read_bytes())
    sha=hashlib.sha256(target.read_bytes()).hexdigest()
    (build/'SHA256SUMS.txt').write_text(f'{sha}  {target.name}\n')
    site=ROOT/'site'
    if site.exists():shutil.rmtree(site)
    shutil.copytree(ROOT/'web',site)
    for directory in ['fonts','specimen']:shutil.copytree(ROOT/directory,site/directory)
    for rel in ['OFL.txt','FONTLOG.txt']:shutil.copy(ROOT/rel,site/rel)
    shutil.copy(target,site/target.name)
    shutil.copy(build/'SHA256SUMS.txt',site/'SHA256SUMS.txt')
    (site/'.nojekyll').touch()
    revision=os.environ.get('GITHUB_SHA','local')
    path=site/'index.html';path.write_text(path.read_text().replace('__REVISION__',revision[:12]))
    coverage=json.loads((ROOT/'specimen/coverage.json').read_text())
    data={'revision':revision,'pages':coverage['pages'],'codepoints':[int(c['codepoint'][2:],16) for c in coverage['characters']]}
    (site/'specimen-data.js').write_text('window.SPECIMEN_DATA = '+json.dumps(data,ensure_ascii=True,separators=(',',':'))+';\n')
    (site/'build.json').write_text(json.dumps({'revision':revision,'font_manifest':json.loads((ROOT/'fonts/manifest.json').read_text())},indent=2)+'\n')
    print(f'Packaged {target.name} ({target.stat().st_size:,} bytes) and site/')

if __name__=='__main__':package()
