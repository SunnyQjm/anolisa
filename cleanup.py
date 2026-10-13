import hashlib,json,os,shutil,subprocess,tomllib
from pathlib import Path
repo=Path('/Users/quejianming/vscode/cosh-shell-dev/.worktrees/codex-cosh-quota-c')
root=Path('/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/data-C');out=root/'round11'
f=json.loads((out/'source-validation-hashes.json').read_text())
c=json.loads((out/'CI-components-final.json').read_text());assert c['headSha']==f['head'] and c['status']=='completed' and c['conclusion']=='success'
pr=json.loads((out/'pr-final-checks.json').read_text());assert pr['headRefOid']==f['head'] and all(x['status']=='COMPLETED' and x['conclusion'] in ['SUCCESS','SKIPPED','NEUTRAL'] for x in pr['statusCheckRollup'])
review=json.loads((out/'review-readback.json').read_text());assert review['full_pagination'] and not review['unresolved_external_changes']
assert all((out/(name+'-final.json')).stat().st_mtime>=(out/'CI-components-final.json').stat().st_mtime for name in ['reviews','review-comments','issue-comments'])
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==f['head']
assert all(hashlib.sha256((repo/n).read_bytes()).hexdigest()==h for n,h in f['source_hashes'].items())
profile=tomllib.loads((root/'round9/container.toml').read_text());cache=root/'round9/cache';assert profile['container']['cache_path']==str(cache) and profile['container']['name']=='codex-data-c-r9-20261014' and not profile['container']['retain'];assert cache.resolve()==cache and cache.is_dir()
ownership=json.loads((out/'cache-ownership-before-cleanup.json').read_text());assert ownership['owner_run']=='20261013T190856Z-2c83db58' and ownership['cache']==str(cache)
env=dict(os.environ,PYTHONPATH='/Users/quejianming/vscode/cosh-shell-dev/.agents/skills/cosh-test-debug-accept/scripts/cosh-lab/src')
cli=['/opt/homebrew/bin/python3.12','-m','cosh_lab','env']
r=subprocess.run([*cli,'down','--run',ownership['owner_run'],'--output','json'],cwd=repo,env=env,capture_output=True,text=True);(out/'cleanup-env-down.json').write_text(r.stdout);assert r.returncode==0 and json.loads(r.stdout)['ok'],r.stderr+r.stdout
r=subprocess.run([*cli,'transport','check','--run',ownership['owner_run'],'--output','json'],cwd=repo,env=env,capture_output=True,text=True);(out/'cleanup-native-status.json').write_text(r.stdout);d=json.loads(r.stdout);assert r.returncode==1 and not d['ok'];probes=d['data']['probes'];assert len(probes)==1 and probes[0]['transport']=='native' and probes[0]['exit_code']==1 and probes[0]['stdout']=='' and probes[0]['stderr']==''
ledger=out/'lab-ledger';assert not ledger.exists();shutil.move(str(repo/'.cosh-lab'),str(ledger))
shutil.rmtree(cache);assert not cache.exists()
assert all(hashlib.sha256((repo/n).read_bytes()).hexdigest()==h for n,h in f['source_hashes'].items())
status=subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip();assert not status,status
home=Path('/Users/quejianming/.copilot-shell/cosh-core/sessions');before=json.loads((root/'round5/host-home-before.json').read_text());after={str(p.relative_to(home)):hashlib.sha256(p.read_bytes()).hexdigest() for p in home.rglob('*') if p.is_file()};proof={'before_count':len(before),'after_count':len(after),'content_map_equal':before==after,'final_cleanup_readback_pending':False};(out/'host-home-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
d={'container_absent':True,'native_probe_exit':1,'owner_run':ownership['owner_run'],'exclusive_cache_deleted':str(cache),'cache_files':ownership['files'],'logical_bytes_reclaimed':ownership['logical_bytes'],'lab_ledger_archived':str(ledger),'worktree_retained':True,'git_clean':True,'all_15_source_hashes_unchanged':True,'host_HOME_416_file_contents_unchanged':before==after,'unrelated_resources_touched':False};(out/'cleanup-final.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d));assert before==after
