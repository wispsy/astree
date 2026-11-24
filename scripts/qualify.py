"""Build receipts and installed behavior checks for wheel and source artifacts."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]

def main():
    directory = Path(sys.argv[1]).resolve()
    profile = sys.argv[2] if len(sys.argv) > 2 else ''
    artifacts = sorted([*directory.glob('*.whl'), *directory.glob('*.tar.gz')])
    if len(artifacts) != 2:
        raise ValueError('Select exactly one wheel and one source distribution')
    for artifact in artifacts:
        with TemporaryDirectory() as temporary:
            outside = Path(temporary)
            environment = outside / 'env'
            subprocess.run(['uv', 'venv', str(environment), '--python', sys.executable], check=True)
            python = environment / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
            target = str(artifact) + (f'[{profile}]' if profile else '')
            subprocess.run(['uv', 'pip', 'install', '--python', str(python), target], check=True, cwd=outside)
            subprocess.run([str(python), '-I', '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v'], check=True, cwd=outside)
            if profile == 'javascript':
                subprocess.run([str(python), '-I', '-c', "from astree.javascript import parse; root=parse('const value = 1;'); assert root.type == 'program' and not root.has_error"], check=True, cwd=outside)
            subprocess.run(['uv', 'pip', 'check' , '--python', str(python)], check=True, cwd=outside)
            print(json.dumps({'artifact': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
                              'profile': profile or 'base', 'python': sys.version.split()[0], 'platform': sys.platform}), flush=True)

if __name__ == '__main__':
    main()
