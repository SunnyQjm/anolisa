import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

if os.environ.get('COSH_9978_DISPOSABLE_CONTAINER') != '1':
    raise SystemExit('requires explicitly selected disposable container')

binary = str(Path(sys.argv[1]).resolve())
work = Path(sys.argv[2]).resolve()
work.mkdir(parents=True, exist_ok=True)
program = Path('/usr/bin/journalctl')
backup = work / 'journalctl.original'
existed = program.exists()
if existed:
    shutil.copy2(program, backup)

fixture = r'''#!/usr/bin/python3
import json, os, re, sys, time
from pathlib import Path
args = sys.argv[1:]
root = Path(os.environ['COSH_9978_CASE_DIR'])
(root / 'invocation.json').write_text(json.dumps(args))
mode = os.environ['COSH_9978_CASE']
if mode == 'failure':
    sys.stderr.write('Failed to open journal: Permission denied\n')
    sys.exit(1)
epoch = int(time.time()) - 30
lines = [f'{epoch}.0 host kernel: driver informational ' + 'x' * 150 for _ in range(197)]
if mode == 'signals':
    lines += [f'{epoch}.0 host kernel: oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/test,task_memcg=/test,task=worker,pid=123,uid=0', f'{epoch}.0 host kernel: Out of memory: Killed process 123 (worker) total-vm:1024kB', f'{epoch}.0 host kernel: Kernel panic - not syncing: regression fixture']
if mode == 'oversized':
    lines = [f'{epoch}.0 host kernel: oom-kill:constraint=CONSTRAINT_MEMCG,task=worker,pid=123 ' + 'x' * 160 for _ in range(200)]
raw = '\n'.join(lines) + '\n'
(root / 'raw-bytes.txt').write_text(str(len(raw.encode())))
pattern = None
for index, arg in enumerate(args):
    if arg == '--grep': pattern = args[index + 1]
    if arg.startswith('--grep='): pattern = arg.split('=', 1)[1]
if pattern is not None:
    lines = [line for line in lines if re.search(pattern, line, re.I)]
if '-n' in args:
    lines = lines[-int(args[args.index('-n') + 1]):]
if lines:
    sys.stdout.write('\n'.join(lines) + '\n')
elif '--quiet' not in args and '-q' not in args:
    sys.stdout.write('-- No entries --\n')
sys.exit(0 if lines else 1)
'''

results = []
try:
    program.write_text(fixture)
    program.chmod(0o755)
    for mode in ['signals', 'empty', 'oversized', 'failure']:
        directory = work / mode
        directory.mkdir(exist_ok=True)
        home = directory / 'home'
        home.mkdir(exist_ok=True)
        bundle = directory / 'bundle.json'
        env = dict(os.environ, HOME=str(home), COSH_9978_CASE=mode,
                   COSH_9978_CASE_DIR=str(directory), COSH_SHELL_LANG='en-US')
        env.pop('COSH_SHELL_HEALTH_SCAN', None)
        result = subprocess.run([binary, 'diagnostics', 'export', '--output', str(bundle)],
                                env=env, capture_output=True, text=True, timeout=30)
        (directory / 'stdout.txt').write_text(result.stdout)
        (directory / 'stderr.txt').write_text(result.stderr)
        health = json.loads(bundle.read_text())['sources']['health']
        facts = {item['key']: item['value'] for item in health['facts']}
        unavailable = [item for item in health['unavailable'] if item['collector'] == 'kernel_signal']
        if mode == 'signals':
            passed = facts.get('kernel.oom_latest_pid') == 123 and facts.get('kernel.oom_killed_process') == 'worker' and facts.get('kernel.panic_recent') is True and not unavailable
        elif mode == 'empty':
            passed = facts.get('kernel.panic_recent') is False and not unavailable and 'kernel_signal' in health['checks_done']
        elif mode == 'oversized':
            passed = any(item['reason'] == 'parse_error' for item in unavailable) and 'kernel.oom_latest_pid' not in facts
        else:
            passed = bool(unavailable) and 'kernel.panic_recent' not in facts
        results.append(dict(case=mode, passed=passed, kernel_facts={key: value for key, value in facts.items() if key.startswith('kernel.')}, unavailable=unavailable, checks_done=health['checks_done']))
finally:
    if existed:
        shutil.copy2(backup, program)
    else:
        program.unlink(missing_ok=True)

(work / 'results.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
raise SystemExit(0 if all(item['passed'] for item in results) else 1)
