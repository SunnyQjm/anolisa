import importlib.util, json, tempfile, hashlib
from pathlib import Path
module_path=Path("/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/ui/pr-assets/resize_render.py")
spec=importlib.util.spec_from_file_location("resize_render",module_path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
root=Path(__file__).parent
results=[]
for metadata_path in (root/"final-native-pty-evidence").rglob("metadata.json"):
 metadata=json.loads(metadata_path.read_text());raw=metadata_path.with_name("transcript.bin").read_bytes()
 _,rows,cols=metadata["geometry"][0]
 with tempfile.TemporaryDirectory(prefix="cosh-native-prompt-replay-") as temporary:
  replay=module.Replay(Path(temporary),cols,rows)
  try:
   cursor=0
   for point in metadata["timeline"]:
    if point["offset"]<cursor: raise ValueError("unordered byte checkpoints")
    replay.feed("o",raw[cursor:point["offset"]].decode("utf-8"));cursor=point["offset"]
    if point["label"]=="native-prompt-recovered":
     snapshot=replay.snapshot()
     record={"test":metadata["test_name"],"source_head":metadata["source_head"],"source_tree":metadata["source_tree"],"shell_sha256":metadata["shell_sha256"],"worker_sha256":metadata["worker_sha256"],"core_sha256":metadata["core_sha256"],"raw_sha256":hashlib.sha256(raw).hexdigest(),"byte_point":point,"execution":"supplemental-tmux-replay-of-original-PTY-bytes","timing":"synthetic; original byte order and geometry retained","screen":snapshot}
     metadata_path.with_name("prompt-screen.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
     assert snapshot["cursor_visible"],record
     assert (snapshot["y"],snapshot["x"])==(31,14),record
     png=module.raster(snapshot,metadata_path.parent,0)
     record["screenshot"]=str(png);results.append(record)
     break
  finally: replay.close()
(root/"native-prompt-replay-summary.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
print(json.dumps([{k:r[k] for k in ["test","source_head","byte_point","screenshot"]} for r in results],ensure_ascii=False))
