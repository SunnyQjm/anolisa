import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

if os.environ.get('COSH_9978_DISPOSABLE_CONTAINER') != '1':
    raise SystemExit('disposable container required')
binary = Path('/tmp/cosh-linux-preflight/diagnostics-v2/cosh-shell')
work = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/cosh-diagnostics-after')
work.mkdir(exist_ok=True)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

journal = Path('/usr/bin/journalctl')
journal_before = digest(journal)
result = subprocess.run([sys.executable, '/tmp/9978-blackbox.py', str(binary), str(work / 'oom')],
                        capture_output=True, text=True, timeout=120)
(work / 'oom.stdout').write_text(result.stdout)
(work / 'oom.stderr').write_text(result.stderr)
if result.returncode:
    raise SystemExit(result.stdout + result.stderr)
assert digest(journal) == journal_before, 'journalctl restoration failed'
oom = json.loads((work / 'oom/results.json').read_text())
program = Path('/usr/bin/df')
backup = work / 'df.original'
shutil.copy2(program, backup)
df_before = digest(program)
fs = []
try:
    for mode, used, root_free, mounts in [
        ('low-small', 4, 39845888, ['/']),
        ('high-efi', 96, 39845888, ['/']),
        ('critical-efi', 4, 39845888, ['/', '/boot/efi']),
        ('root-custom', 4, 1048576, ['/data']),
    ]:
        directory = work / mode
        home = directory / 'home'
        config = home / '.copilot-shell'
        config.mkdir(parents=True, exist_ok=True)
        (config / 'config.toml').write_text('[health]\ncritical_mounts = ' + json.dumps(mounts) + '\n')
        root_total, root_used = (1103764, 55188) if mode == 'root-custom' else (41943040, 2097152)
        efi_used, efi_free = (196608, 8192) if used == 96 else (8192, 196608)
        rows = ['Filesystem Type 1024-blocks Used Available Capacity Mounted on',
                f'/dev/root ext4 {root_total} {root_used} {root_free} 5% /',
                f'/dev/efi vfat 204800 {efi_used} {efi_free} {used}% /boot/efi',
                'efivarfs efivarfs 256 8 248 3% /sys/firmware/efi/efivars',
                '/dev/small ext4 1398100 559240 838860 40% /small-data']
        program.write_text('#!/usr/bin/python3\nprint(' + repr('\n'.join(rows)) + ')\n')
        program.chmod(0o755)
        env = dict(os.environ, HOME=str(home), COSH_SHELL_LANG='en-US')
        env.pop('COSH_SHELL_HEALTH_SCAN', None)
        bundle = directory / 'bundle.json'
        completed = subprocess.run([str(binary), 'diagnostics', 'export', '--output', str(bundle)],
                                   capture_output=True, text=True, env=env, timeout=30)
        assert completed.returncode == 0, completed.stderr
        health = json.loads(bundle.read_text())['sources']['health']
        assert any(item['key'] == 'filesystem.mount./boot/efi.used_ratio' for item in health['facts']), 'fixture mount not collected'
        findings = [item for item in health['findings'] if item['id'].startswith(('J09', 'J10'))]
        if mode == 'low-small':
            passed = not findings
        elif mode in ('high-efi', 'critical-efi'):
            passed = any(item['id'] == 'J09:/boot/efi' for item in findings)
        else:
            passed = any(item['id'] == 'J09' for item in findings)
        fs.append({'case': mode, 'passed': passed, 'findings': findings})
finally:
    shutil.copy2(backup, program)
assert digest(program) == df_before, 'df restoration failed'
manifest = {'execution': 'deterministic', 'binary': str(binary), 'binary_sha256': digest(binary),
            'journalctl_restored': digest(journal) == journal_before, 'df_restored': digest(program) == df_before,
            'oom': oom, 'filesystem': fs}
(work / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('Current binary: ' + digest(binary))
print('Deterministic replay; no real OOM injection')
for item in oom:
    print('OOM ' + item['case'] + ': ' + ('PASS' if item['passed'] else 'FAIL'))
for item in fs:
    print('Filesystem ' + item['case'] + ': ' + ('PASS' if item['passed'] else 'FAIL'))
print('journalctl/df restored and SHA256 verified')
passed = all(item['passed'] for item in oom + fs)
print('8 deterministic cases passed' if passed else 'deterministic replay FAILED')
raise SystemExit(0 if passed else 1)
