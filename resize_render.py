from __future__ import annotations

import base64
import errno
import hashlib
import json
import math
import os
import re
from pathlib import Path
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile
import time


def run(argv):
    result = subprocess.run(argv, capture_output=True, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace').strip())
    return result.stdout


def read_cast(path):
    lines = path.read_text().splitlines()
    header, events = json.loads(lines[0]), [json.loads(line) for line in lines[1:] if line]
    if header.get('version') != 2 or any(type(header.get(key)) is not int or not 1 <= header[key] <= 1000 for key in ['width', 'height']):
        raise ValueError('resize replay requires valid asciicast v2 geometry')
    previous = 0
    for event in events:
        if not isinstance(event, list) or len(event) != 3:
            raise ValueError('invalid cast event shape')
        timestamp, kind, data = event
        if type(timestamp) not in {int, float} or not math.isfinite(timestamp) or timestamp < previous:
            raise ValueError('cast events are not finite and ordered')
        previous = timestamp
        if kind not in {'o', 'r', 'i', 'm'} or not isinstance(data, str):
            raise ValueError('invalid cast event type or data')
        if kind == 'r':
            if not re.fullmatch(r'[0-9]+x[0-9]+', data):
                raise ValueError('invalid resize geometry')
            cols, rows = map(int, data.split('x'))
            if min(cols, rows) < 1 or max(cols, rows) > 1000:
                raise ValueError('invalid resize geometry')
    return header, events


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Replay:
    def __init__(self, root, cols, rows):
        self.root = root
        self.socket = root / 'tmux.sock'
        self.fifo, self.ack = root / 'input', root / 'ack'
        os.mkfifo(self.fifo)
        self.ack.write_text('0')
        worker = root / 'writer.py'
        worker.write_text("import sys,json,base64\nfrom pathlib import Path\nwith open(sys.argv[1]) as stream:\n for line in stream:\n  event=json.loads(line)\n  sys.stdout.buffer.write(base64.b64decode(event['data']))\n  sys.stdout.buffer.flush()\n  Path(sys.argv[2]).write_text(str(event['id']))\n")
        command = 'stty -echo -onlcr; exec ' + shlex.join([sys.executable, str(worker), str(self.fifo), str(self.ack)])
        self.pid = None
        self.closed = False
        try:
            self.tmux('new-session', '-d', '-x', str(cols), '-y', str(rows), command)
            self.pid = int(self.tmux('display-message', '-p', '#{pane_pid}').strip())
            self.tmux('set-option', '-g', 'status', 'off')
            self.tmux('set-option', '-g', 'history-limit', '10000')
            self.tmux('set-window-option', '-g', 'window-size', 'manual')
            deadline = time.monotonic() + 5
            while True:
                try:
                    fd = os.open(self.fifo, os.O_WRONLY | os.O_NONBLOCK)
                    self.stream = os.fdopen(fd, 'w')
                    break
                except OSError as error:
                    if error.errno != errno.ENXIO or time.monotonic() > deadline:
                        raise
                    time.sleep(0.005)
            self.sequence = 0
        except BaseException:
            self.close()
            raise

    def tmux(self, *args):
        return run(['tmux', '-S', str(self.socket), *args]).decode('utf-8')

    def feed(self, kind, data):
        if kind == 'r':
            cols, rows = data.split('x')
            self.tmux('resize-window', '-x', cols, '-y', rows)
        elif kind == 'o':
            self.sequence += 1
            self.stream.write(json.dumps({'id': self.sequence, 'data': base64.b64encode(data.encode()).decode()}) + '\n')
            self.stream.flush()
            deadline = time.monotonic() + 5
            while self.ack.read_text() != str(self.sequence):
                if time.monotonic() > deadline:
                    raise RuntimeError('PTY writer acknowledgement timed out')
                time.sleep(0.005)

    def snapshot(self):
        previous = None
        stable = 0
        deadline = time.monotonic() + 5
        while stable < 3:
            grid = self.tmux('capture-pane', '-p', '-e')
            state = self.tmux('display-message', '-p', '#{pane_width} #{pane_height} #{cursor_x} #{cursor_y} #{cursor_flag}')
            current = (grid, state)
            stable = stable + 1 if current == previous else 0
            previous = current
            if time.monotonic() > deadline:
                raise RuntimeError('tmux terminal state did not settle')
            time.sleep(0.01)
        cols, rows, x, y, visible = map(int, state.split())
        plain = self.tmux('capture-pane', '-p')
        history = self.tmux('capture-pane', '-p', '-S', '-', '-J')
        return {'cols': cols, 'rows': rows, 'x': x, 'y': y, 'cursor_visible': bool(visible), 'grid': grid, 'plain': plain, 'history': history}

    def close(self):
        if self.closed:
            return
        if hasattr(self, 'stream'):
            self.stream.close()
        result = subprocess.run(['tmux', '-S', str(self.socket), 'kill-server'], capture_output=True, timeout=10)
        deadline = time.monotonic() + 5
        while True:
            probe = subprocess.run(['tmux', '-S', str(self.socket), 'list-sessions'], capture_output=True, timeout=5)
            writer = subprocess.run(['ps', '-p', str(self.pid), '-o', 'stat='], capture_output=True) if self.pid else None
            ended = writer is None or not writer.stdout.strip() or writer.stdout.strip().startswith(b'Z')
            if probe.returncode != 0 and ended:
                self.closed = True
                return
            if time.monotonic() > deadline:
                raise RuntimeError('owned tmux server/writer cleanup failed: ' + result.stderr.decode(errors='replace'))
            time.sleep(0.01)


def raster(snapshot, root, number):
    # This is a rendering-only grid projection, never a replacement recording.
    projection = '\x18\x1b[?7l\x1b[0m\x1b[2J'
    for row, line in enumerate(snapshot['grid'].splitlines(), 1):
        projection += f'\x1b[{row};1H' + line
    projection += f"\x1b[0m\x1b[{snapshot['y'] + 1};{snapshot['x'] + 1}H"
    projection += '\x1b[?25h' if snapshot['cursor_visible'] else '\x1b[?25l'
    cast = root / f'projection-{number}.cast'
    cast.write_text(json.dumps({'version': 2, 'width': snapshot['cols'], 'height': snapshot['rows'], 'derived_intermediate': 'tmux grid raster projection'}) + '\n' + json.dumps([0, 'o', projection]) + '\n')
    gif, png = root / f'projection-{number}.gif', root / f'frame-{number}.png'
    run(['agg', '--quiet', '--no-loop', '--renderer', 'resvg', '--select', '100%', str(cast), str(gif)])
    run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(gif), '-frames:v', '1', str(png)])
    return png


def png_size(path):
    return struct.unpack('>II', path.read_bytes()[16:24])


def render(run_dir, case_id, points):
    for tool in ['tmux', 'agg', 'ffmpeg', 'ffprobe']:
        if shutil.which(tool) is None:
            raise RuntimeError(f'{tool} is required for faithful resize replay')
    source = run_dir / 'transcript.cast'
    header, events = read_cast(source)
    source_hash = digest(source)
    manifest = json.loads((run_dir / 'run.json').read_text())
    head = manifest.get('repo', {}).get('commit')
    screenshots, screens, provenance = run_dir / 'screenshots', run_dir / 'screens', run_dir / 'render-provenance'
    for directory in [screenshots, screens, provenance]:
        directory.mkdir(exist_ok=True)
    last_ms = math.ceil(events[-1][0] * 1000)
    for point in points:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}', point['id']):
            raise ValueError('unsafe acceptance point id')
    targets = {point['id']: min(max(point['offset_ms'], 0), last_ms) for point in points}
    with tempfile.TemporaryDirectory(prefix='cosh-resize-render-') as temporary:
        root = Path(temporary)
        replay = Replay(root, header['width'], header['height'])
        snapshots = []
        try:
            snapshots.append({'source_time': 0, 'source_event': 0, **replay.snapshot()})
            for index, (timestamp, kind, data) in enumerate(events, 1):
                if kind in {'o', 'r'}:
                    replay.feed(kind, data)
                    snapshots.append({'source_time': timestamp, 'source_event': index, **replay.snapshot()})
        finally:
            replay.close()
        # WebM stores milliseconds. Ceil never advances a future event into the past.
        frames = {}
        for snapshot in snapshots:
            frames[math.ceil(snapshot['source_time'] * 1000)] = snapshot
        cache = {}
        for index, (pts, snapshot) in enumerate(sorted(frames.items())):
            key = json.dumps({key: value for key, value in snapshot.items() if key not in {'source_time', 'source_event', 'history'}}, sort_keys=True)
            if key not in cache:
                cache[key] = raster(snapshot, root, index)
            snapshot['png'] = cache[key]
            snapshot['pts_ms'] = pts
        canvas = tuple(max(png_size(snapshot['png'])[axis] for snapshot in frames.values()) for axis in [0, 1])
        frame_map = []
        concat = root / 'frames.txt'
        entries = []
        ordered = sorted(frames.items())
        for index, (pts, snapshot) in enumerate(ordered):
            padded = root / f'padded-{index}.png'
            run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(snapshot['png']), '-vf', f'pad={canvas[0]}:{canvas[1]}:0:0:color=0x282a36', '-frames:v', '1', str(padded)])
            next_pts = ordered[index + 1][0] if index + 1 < len(ordered) else last_ms + 3000
            entries += [f'file {shlex.quote(str(padded))}', 'option framerate 1000', f'duration {(next_pts - pts) / 1000:.3f}']
            frame_map.append({'source_event': snapshot['source_event'], 'source_time_seconds': snapshot['source_time'], 'pts_ms': pts, 'viewport': [snapshot['cols'], snapshot['rows']], 'image_size': list(png_size(snapshot['png']))})
        entries += [f'file {shlex.quote(str(padded))}', 'option framerate 1000']
        concat.write_text('\n'.join(entries) + '\n')
        movie = root / 'replay.webm'
        run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat), '-fps_mode', 'passthrough', '-enc_time_base', '1:1000', '-c:v', 'libvpx-vp9', '-lossless', '1', '-pix_fmt', 'yuv444p', str(movie)])
        probe = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'frame=pts_time', '-of', 'json', str(movie)]))
        encoded = [round(float(frame['pts_time']) * 1000) for frame in probe['frames']]
        expected = [pts for pts, _ in ordered]
        if encoded[:len(expected)] != expected:
            raise RuntimeError(f'encoded frame clock differs from source map: {encoded} != {expected}')
        result = []
        for point in points:
            target = targets[point['id']]
            state = max((state for state in snapshots if state['source_time'] * 1000 <= target), key=lambda state: state['source_event'])
            if 'png' not in state:
                state['png'] = raster(state, root, f"point-{point['id']}")
            png = screenshots / f"{point['id']}.png"
            shutil.copyfile(state['png'], png)
            row = {'case_id': case_id, 'acceptance_point_id': point['id'], 'cast_offset_ms': target, 'source_sha256': source_hash, 'screenshot': str(png.relative_to(run_dir)), 'screenshot_sha256': digest(png), 'layout_sensitive': str(bool(point.get('layout_sensitive', False))).lower(), 'screen': '', 'screen_sha256': '', 'screen_source': ''}
            if point.get('layout_sensitive', False):
                video = screens / f"{point['id']}.webm"
                shutil.copyfile(movie, video)
                row.update(screen=str(video.relative_to(run_dir)), screen_sha256=digest(video), screen_source='cast-replay')
            detail = {'schema_version': 1, 'renderer': 'tmux-grid/agg-resvg-static-projection', 'tmux_version': run(['tmux', '-V']).decode().strip(), 'agg_version': run(['agg', '--version']).decode().strip(), 'source_sha256': source_hash, 'source_head': head, 'point_id': point['id'], 'cast_offset_ms': target, 'source_event': state['source_event'], 'viewport': [state['cols'], state['rows']], 'png_dimensions': list(png_size(png)), 'canvas_dimensions': list(canvas), 'screenshot_sha256': digest(png), 'screen_sha256': row['screen_sha256'], 'video_time_mapping': 'source origin0; ceil milliseconds; same-ms events keep last state; no future event early; 3s terminal tail', 'frames': frame_map, 'encoded_pts_ms': encoded, 'derived_intermediate': 'temporary terminal-grid projection; original cast unchanged', 'screen_text': state['plain'], 'logical_history': state['history'], 'cleanup': 'isolated tmux server killed; FIFO/writer/temp files removed'}
            path = provenance / f"{point['id']}.json"
            path.write_text(json.dumps(detail, indent=2, ensure_ascii=False) + '\n')
            row.update(replay_provenance=str(path.relative_to(run_dir)), replay_provenance_sha256=digest(path))
            result.append(row)
    if digest(source) != source_hash:
        raise RuntimeError('source cast changed during render')
    return result


def validate_provenance(run_dir, row, manifest):
    path = (run_dir / row.get('replay_provenance', '')).resolve()
    if not path.is_relative_to(run_dir.resolve()) or not path.is_file():
        raise ValueError('missing or unsafe resize replay provenance')
    if digest(path) != row.get('replay_provenance_sha256'):
        raise ValueError('resize replay provenance hash mismatch')
    proof = json.loads(path.read_text())
    header, events = read_cast(run_dir / 'transcript.cast')
    target = int(row['cast_offset_ms'])
    expected = {0: (0, [header['width'], header['height']])}
    geometry = expected[0][1]
    selected = (0, geometry)
    for index, (timestamp, kind, data) in enumerate(events, 1):
        if kind == 'r':
            geometry = list(map(int, data.split('x')))
        if kind in {'o', 'r'}:
            expected[math.ceil(timestamp * 1000)] = (index, geometry)
            if timestamp * 1000 <= target:
                selected = (index, geometry)
    actual_map = [(item['pts_ms'], item['source_event'], item['viewport']) for item in proof['frames']]
    expected_map = [(pts, index, viewport) for pts, (index, viewport) in sorted(expected.items())]
    checks = [
        proof['schema_version'] == 1,
        proof['source_sha256'] == digest(run_dir / 'transcript.cast') == row['source_sha256'],
        proof['source_head'] == manifest.get('repo', {}).get('commit'),
        proof['point_id'] == row['acceptance_point_id'],
        proof['cast_offset_ms'] == target,
        (proof['source_event'], proof['viewport']) == selected,
        proof['png_dimensions'] == list(png_size(run_dir / row['screenshot'])),
        proof['screenshot_sha256'] == row['screenshot_sha256'],
        proof['screen_sha256'] == row['screen_sha256'],
        actual_map == expected_map,
        proof['encoded_pts_ms'][:len(expected_map)] == [item[0] for item in expected_map],
        proof['cleanup'] == 'isolated tmux server killed; FIFO/writer/temp files removed',
    ]
    if not all(checks):
        raise ValueError('resize replay source/time/geometry provenance mismatch')
