"""Package indexed course files, excluding archives, credentials and caches.

Run in a Git checkout after staging intended files. Does not stage or commit.
The generated ZIP and its sidecar are excluded from their own contents.
"""
from pathlib import Path, PurePosixPath
import hashlib, json, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[1]
VERSION='1.1'
PREFIX=f'Agents-Basics-Course-v{VERSION}'
OUTPUT=ROOT/f'output/distribution/Agents-Basics-Full-Course-v{VERSION}.zip'
EXCLUDE_PARTS={'.git','.venv','venv','node_modules','__pycache__','.deck-build','.course-build','.ipynb_checkpoints'}

def eligible(name):
    p=PurePosixPath(name)
    return (not any(v in EXCLUDE_PARTS for v in p.parts)
        and not name.startswith('output/distribution/')
        and p.name not in {'.DS_Store','raw_response.json'}
        and not p.suffix.lower() in {'.zip','.pyc'}
        and not (p.name.startswith('.env') and p.name!='.env.example'))

def main():
    names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    paths=sorted(set(n for n in names if n and eligible(n)))
    required=['START-HERE.md','PACKAGE-CONTENTS.md','teaching/SPEAKER_NOTES.md',
        'output/pptx/MCP_Weather_Teaching_Deck.pptx',
        'mcp-weather-2hour-v1/colab/MCP_Weather_2Hour_Colab.ipynb']
    required += ['output/pdf/MCP_Colab_Student_Workbook'+suffix+'.pdf' for suffix in ('','_JA','_ZH_CN')]
    for name in required:
        if name not in paths:raise ValueError('Required file is not indexed: '+name)
    payload={}
    for name in paths:
        path=ROOT/name
        if path.is_symlink() or not path.is_file():raise ValueError('Not a regular file: '+name)
        data=path.read_bytes()
        if path.suffix=='.ipynb':
            nb=json.loads(data)
            assert all(not c.get('outputs') and c.get('execution_count') is None for c in nb['cells'] if c['cell_type']=='code'),name
        payload[name]=data
    manifest=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in payload.items())
    payload['SHA256SUMS.txt']=manifest.encode()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in payload.items():
            info=zipfile.ZipInfo(PREFIX+'/'+name,date_time=(2026,9,10,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,data)
    with zipfile.ZipFile(OUTPUT) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(payload)
        for name,data in payload.items():assert z.read(PREFIX+'/'+name)==data,name
    digest=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    OUTPUT.with_suffix('.zip.sha256').write_text(digest+'  '+OUTPUT.name+'\n')
    print(OUTPUT)
    print(f'{len(payload)} files; {OUTPUT.stat().st_size:,} bytes; SHA-256 {digest}')
if __name__=='__main__':main()
