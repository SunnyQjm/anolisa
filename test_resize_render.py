from __future__ import annotations

import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest

from cosh_lab.evidence import render_point_screenshots

ORIGINAL = Path('/Users/quejianming/vscode/cosh-shell-dev/outputs/login-shell-golive/ui-approval-slice-runs/20261013T162657Z-b5e5a40d')


def dimensions(path):
    return struct.unpack('>II', path.read_bytes()[16:24])


class ResizeRenderBehavior(unittest.TestCase):
    def test_original_cast_resize_changes_native_png_dimensions(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            shutil.copyfile(ORIGINAL / 'transcript.cast', run / 'transcript.cast')
            shutil.copyfile(ORIGINAL / 'run.json', run / 'run.json')
            points = json.loads((ORIGINAL / 'acceptance-points.json').read_text())
            selected = [point for point in points if point['id'] in {'cjk-output', 'resized-current-card'}]
            rows = render_point_screenshots(run, 'UI-CANONICAL-RESIZE-001', selected)
            before = dimensions(run / rows[0]['screenshot'])
            after = dimensions(run / rows[1]['screenshot'])
            self.assertLess(after[0], before[0], '47-column viewport must not remain80 columns')
            self.assertLess(after[1], before[1], '20-row viewport must not remain30 rows')
            self.assertEqual((run / 'transcript.cast').read_bytes(), (ORIGINAL / 'transcript.cast').read_bytes())


class ResizeModelControls(unittest.TestCase):
    def test_deny_cutoff_ed3_history_and_provenance_negative(self):
        from cosh_lab.resize_render import render, validate_provenance
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            events = [
                [0.001, 'o', 'HISTORY_SENTINEL_abcdefgh终端输出\r\n' * 12],
                [0.2, 'r', '47x20'],
                [0.3, 'o', '\x1b[2J\x1b[H> [ Deny ]'],
                [0.662973, 'o', '\x1b[2J\x1b[H> [ Allow once ]'],
                [0.8, 'o', '\x1b[3J'],
            ]
            (run / 'transcript.cast').write_text(json.dumps({'version': 2, 'width': 80, 'height': 8}) + '\n' + '\n'.join(map(json.dumps, events)) + '\n')
            manifest = {'repo': {'commit': 'a' * 40}}
            (run / 'run.json').write_text(json.dumps(manifest))
            rows = render(run, 'MODEL', [{'id': 'deny', 'offset_ms': 651, 'layout_sensitive': True}, {'id': 'after-ed3', 'offset_ms': 810, 'layout_sensitive': True}])
            proof = json.loads((run / rows[0]['replay_provenance']).read_text())
            self.assertIn('> [ Deny ]', proof['screen_text'])
            self.assertNotIn('> [ Allow once ]', proof['screen_text'])
            self.assertIn('HISTORY_SENTINEL_', proof['logical_history'])
            after = json.loads((run / rows[1]['replay_provenance']).read_text())
            self.assertNotIn('HISTORY_SENTINEL_', after['logical_history'], 'ED3 must actually clear saved history')
            self.assertEqual(proof['viewport'], [47, 20])
            self.assertGreaterEqual(next(frame['pts_ms'] for frame in proof['frames'] if frame['source_event'] == 4), 663)
            validate_provenance(run, rows[0], manifest)
            from cosh_lab.resize_render import run as run_tool
            held = max(index for index, pts in enumerate(proof['encoded_pts_ms']) if pts <= 651)
            width, height = proof['png_dimensions']
            video_pixels = run_tool(['ffmpeg', '-loglevel', 'error', '-i', str(run / rows[0]['screen']), '-vf', f'select=eq(n\\,{held}),crop={width}:{height}:0:0', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
            png_pixels = run_tool(['ffmpeg', '-loglevel', 'error', '-i', str(run / rows[0]['screenshot']), '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
            self.assertEqual(len(video_pixels), len(png_pixels))
            self.assertLessEqual(max(abs(left - right) for left, right in zip(video_pixels, png_pixels)), 3, 'last PTS at cutoff must show the Deny PNG state')
            with self.assertRaisesRegex(ValueError, 'provenance mismatch'):
                validate_provenance(run, rows[0], {'repo': {'commit': 'b' * 40}})

    def test_unordered_resize_rejected(self):
        from cosh_lab.resize_render import read_cast
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'bad.cast'
            path.write_text('{"version":2,"width":80,"height":30}\n[1,"r","47x20"]\n[0.5,"o","late"]\n')
            with self.assertRaisesRegex(ValueError, 'ordered'):
                read_cast(path)

class CleanupControls(unittest.TestCase):
    def test_failed_kill_cannot_claim_cleanup_success(self):
        import subprocess
        from unittest.mock import patch
        from cosh_lab import resize_render
        real_run = subprocess.run
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            replay = resize_render.Replay(root, 80, 30)
            replay.tmux('set-option', '-g', 'remain-on-exit', 'on')
            def reject_kill(argv, **kwargs):
                if 'kill-server' in argv:
                    return subprocess.CompletedProcess(argv, 1, b'', b'injected kill failure')
                return real_run(argv, **kwargs)
            try:
                with patch.object(resize_render.subprocess, 'run', side_effect=reject_kill):
                    with self.assertRaisesRegex(RuntimeError, 'cleanup failed'):
                        replay.close()
                self.assertFalse(replay.closed)
            finally:
                real_run(['tmux', '-S', str(root / 'tmux.sock'), 'kill-server'], capture_output=True, check=True)
            probe = real_run(['tmux', '-S', str(root / 'tmux.sock'), 'list-sessions'], capture_output=True)
            self.assertNotEqual(probe.returncode, 0)

    def test_constructor_failure_closes_actual_owned_server(self):
        from unittest.mock import patch
        from cosh_lab import resize_render
        real_run = resize_render.run
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def fail_real_option(argv):
                if 'set-option' in argv:
                    return real_run(argv[:3] + ['set-option', '-g', 'not-a-real-option', 'on'])
                return real_run(argv)
            with patch.object(resize_render, 'run', side_effect=fail_real_option):
                with self.assertRaises(RuntimeError):
                    resize_render.Replay(root, 80, 30)
            import subprocess
            probe = subprocess.run(['tmux', '-S', str(root / 'tmux.sock'), 'list-sessions'], capture_output=True)
            self.assertNotEqual(probe.returncode, 0, 'owned server must actually disappear')

    def test_input_contract_rejects_boolean_geometry_and_nonstring_output(self):
        from cosh_lab.resize_render import read_cast
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'invalid.cast'
            for header, event in [({'version': 2, 'width': True, 'height': 30}, [0, 'o', 'ok']), ({'version': 2, 'width': 80, 'height': 30}, [0, 'o', 3])]:
                path.write_text(json.dumps(header) + '\n' + json.dumps(event) + '\n')
                with self.assertRaises(ValueError):
                    read_cast(path)


if __name__ == '__main__':
    unittest.main()
