import hashlib,json,os,shlex,subprocess
from pathlib import Path
repo=Path('/Users/quejianming/vscode/cosh-shell-dev/.worktrees/codex-cosh-quota-c')
out=Path('/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/data-C/round11')
core=repo/'src/cosh-ng/crates/cosh-core/src'
files={'store':core/'session/store.rs','budget':core/'session/store/budget.rs','scoped':core/'session/scoped.rs','engine':core/'compaction/engine.rs','headless':core/'headless.rs'}
original={key:path.read_text() for key,path in files.items()}
baseline=json.loads((out/'source-validation-hashes.json').read_text())
assert all(hashlib.sha256((repo/name).read_bytes()).hexdigest()==sha for name,sha in baseline['source_hashes'].items())
env=dict(os.environ,PYTHONPATH='/Users/quejianming/vscode/cosh-shell-dev/.agents/skills/cosh-test-debug-accept/scripts/cosh-lab/src')
def replace(s, old, new):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new, 1)

def clock_only(s):
    a = s.index('fn envelope_commit_clock(')
    b = s.index('\nfn persist_dir_is_workspace_relative', a)
    return s[:a] + 'fn envelope_commit_clock(bytes: &[u8], _id: &ProviderSessionId, _scope: &Path) -> Option<u64> { serde_json::from_slice::<serde_json::Value>(bytes).ok()?.get("updated_at_ms")?.as_u64() }\n' + s[b:]

def incomplete_schema(s):
    a = s.index('fn envelope_commit_clock(')
    b = s.index('\nfn persist_dir_is_workspace_relative', a)
    return s[:a] + 'fn envelope_commit_clock(bytes: &[u8], id: &ProviderSessionId, scope: &Path) -> Option<u64> {\n let value:serde_json::Value=serde_json::from_slice(bytes).ok()?;\n if value["schema_version"].as_u64()? != u64::from(CURRENT_SCHEMA_VERSION) || value["session_id"].as_str()? != id.as_str() { return None; }\n let workspace=value["workspace_scope"].as_str()?;\n let expected=hex::encode(sha2::Sha256::digest(workspace.as_bytes()));\n if scope.file_name()?.to_str()? != &expected[..SCOPE_DIR_NAME_LEN] { return None; }\n value["updated_at_ms"].as_u64()\n}\n' + s[b:]

def mismatched_id(s):
    return replace(s, 'let envelope = parse_modern_session(id, serde_json::from_slice(bytes).ok()?).ok()?;', 'let value:serde_json::Value=serde_json::from_slice(bytes).ok()?; let own:ProviderSessionId=serde_json::from_value(value["session_id"].clone()).ok()?; let envelope = parse_modern_session(&own, value).ok()?; let _ = id;')

def workspace_hash(s):
    return replace(s, 'if scope.file_name()?.to_str()? != &expected[..SCOPE_DIR_NAME_LEN] {', 'if false && scope.file_name()?.to_str()? != &expected[..SCOPE_DIR_NAME_LEN] {')

def index_version(s):
    return replace(s, 'if index.schema_version != INDEX_SCHEMA_VERSION {', 'if false && index.schema_version != INDEX_SCHEMA_VERSION {')

def omit_marker_bytes(s):
 return replace(s,'generation.matches_directory_metadata(&pinned_metadata)','generation.matches(&legacy.file)')
def empty_workspace(s):
 return replace(s,'            if location.legacy.is_empty() {\n                continue;\n            }\n','')
def compact_unleased(s):
 a=s.index('    let _activity =');b=s.index('    // 1. Snapshot:',a)
 return s[:a]+s[b:]
def compact_runtime_lease(s):
 return replace(s,'.acquire_compaction_lease(session_id)','.acquire_live_lease(session_id)')
def compact_probe_absent(s):
 return replace(s,'        guards.last_mut()?.acquire_compaction().ok()?;\n','')
def compact_cleanup_absent(s):
 a=s.index("impl Drop for CompactionLease<'_> {");b=s.index('\nimpl SessionStore',a)
 return s[:a]+"impl Drop for CompactionLease<'_> { fn drop(&mut self) {} }\n"+s[b:]
def missing_registration(s):
 return replace(s,'.acquire_resume_live_lease(&session_id)','.acquire_live_lease(&session_id)')
def activity_sweep_restored(s):
 return replace(s,'activity.activity_directory().ok().flatten()?','activity.directory(true).ok().flatten()?')
cases=[
 ('modern_clock_only','store',clock_only,'--bin','cosh-core','session::store::tests::modern_budget_preserves_unreadable_envelopes','unsupported or corrupt envelope must survive budget sweeping'),
 ('modern_incomplete_schema','store',incomplete_schema,'--bin','cosh-core','session::store::tests::modern_budget_preserves_unreadable_envelopes','unsupported or corrupt envelope must survive budget sweeping'),
 ('modern_mismatched_id','store',mismatched_id,'--bin','cosh-core','session::store::tests::modern_budget_preserves_unreadable_envelopes','unsupported or corrupt envelope must survive budget sweeping'),
 ('modern_workspace_hash','store',workspace_hash,'--bin','cosh-core','session::store::tests::modern_budget_preserves_unreadable_envelopes','unsupported or corrupt envelope must survive budget sweeping'),
 ('owned_marker_bytes_omitted','budget',omit_marker_bytes,'--test','session_recovery','quota::lost_legacy_deletion_markers_keep_same_directory_bytes_in_the_user_budget','lost deletion proof must not make owned bytes disappear from the quota'),
 ('empty_legacy_workspace_opened','budget',empty_workspace,'--test','session_recovery','quota::stale_workspace_without_legacy_ownership_does_not_block_another_workspace','no-legacy historical workspace must not block persistence'),
 ('compaction_source_unleased','engine',compact_unleased,'--test','compaction_activity','blocked_compaction_survives_another_process_age_sweep','age sweep removed the in-flight compaction session'),
 ('compaction_runtime_self_conflict','engine',compact_runtime_lease,'--bin','cosh-core','compaction::engine::tests::compaction_coexists_with_the_runtime_live_lease',''),
 ('compaction_probe_removed','store',compact_probe_absent,'--test','compaction_activity','blocked_compaction_survives_another_process_age_sweep','age sweep removed the in-flight compaction session'),
 ('compaction_cancel_cleanup_removed','store',compact_cleanup_absent,'--bin','cosh-core','compaction::engine::tests::cancelled_compaction_releases_its_created_activity_lease',''),
 ('missing_resume_registration_restored','headless',missing_registration,'--test','session_recovery','resume_absence::missing_resumes_across_workspaces_preserve_directories_and_location_index','missing resume 0 registered a workspace'),
 ('activity_directory_resweep_restored','store',activity_sweep_restored,'--bin','cosh-core','session::store::tests::budget_activity_probes_do_not_rescan_temporary_files_per_candidate','budget activity probes must not rescan temporary files'),
 ('old_private_schema_accepted','budget',index_version,'--bin','cosh-core','session::store::tests::old_or_unknown_location_index_versions_preserve_index_and_data','called `Result::unwrap_err()` on an `Ok` value')]
records=[]
try:
 for name,key,mutate,flag,target,case,proof in cases:
  for key0,path in files.items():path.write_text(original[key0])
  files[key].write_text(mutate(original[key]))
  command='python3 /cache/r10-mutant-payload/mutation_runner.py '+shlex.join([flag,target,case])
  r=subprocess.run(['/opt/homebrew/bin/python3.12','-m','cosh_lab','env','exec','--run','20261013T190856Z-2c83db58','--output','json','--','sh','-c',command],cwd=repo,env=env,capture_output=True,text=True)
  (out/('mutant-'+name+'.json')).write_text(r.stdout)
  data=json.loads(r.stdout)['data'];log=data['stdout']+data['stderr']
  bindings=[json.loads(line.split('=',1)[1]) for line in data['stdout'].splitlines() if line.startswith('artifact_binding=')]
  expected={str(path.relative_to(repo/'src/cosh-ng')):hashlib.sha256(path.read_bytes()).hexdigest() for path in files.values()}
  bound=len(bindings)==1 and bindings[0]['source_sha256']==expected
  compiled='Finished `test` profile' in log and 'running 1 test' in log and bound
  kill=compiled and data['exit_code']==101 and (proof in log if proof else case in log and 'FAILED' in log)
  record=dict(name=name,compiled=compiled,valid_behavioral_kill=kill,exit_code=data['exit_code'],expected_failure=proof,compiled_source_binding=bound,artifact_binding=bindings[0] if bindings else None,baseline_head=baseline['head'])
  records.append(record);print(json.dumps(record),flush=True);assert kill
finally:
 for key,path in files.items():path.write_text(original[key])
 (out/'mutant-summary.json').write_text(json.dumps(dict(baseline_head=baseline['head'],baseline_tree=baseline['tree'],results=records,sources_restored=all(path.read_text()==original[key] for key,path in files.items())),indent=2)+'\n')
