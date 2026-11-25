#!/usr/bin/env python3
"""Regenerate demos/sparks/ from the upstream Sparks app as a cut of N games.
Usage: python3 tools/cut-sparks.py stroop driftwatch nback ration mirror
Copies fonts/icons/manifest, rewrites the home link, and limits the grid,
Surprise-me, and saved-game state to the chosen ids. Everything else is upstream verbatim."""
import sys, json, shutil, pathlib, re
SRC = pathlib.Path.home()/'jakes-workshop'/'sparks'
DST = pathlib.Path(__file__).resolve().parents[1]/'demos'/'sparks'
ids = sys.argv[1:] or ['stroop','driftwatch','nback','ration','mirror']
s = (SRC/'index.html').read_text()
def rep(old, new, count=None):
    global s; n = s.count(old); assert n, f'not found: {old[:70]}'
    if count: assert n == count, (old[:50], n)
    s = s.replace(old, new)
# sanity: every id exists upstream
have = set(re.findall(r'\{id:"([a-z]+)"', s)); missing = [i for i in ids if i not in have]; assert not missing, f'unknown ids: {missing}'
rep('<a class="iconbtn homelink" href="../" title="All apps"', '<a class="iconbtn homelink" href="../../" title="All apps"', 1)
rep('{id:"illumination", icon:"📜", name:"Illumination", tag:"find the sacred symbol"},\n];',
    '{id:"illumination", icon:"📜", name:"Illumination", tag:"find the sacred symbol"},\n];\nconst DEMO_ONLY=new Set(%s);\nconst DEMO_GAMES=GAMES.filter(g=>DEMO_ONLY.has(g.id));' % json.dumps(ids), 1)
rep('GAMES[Math.floor(Math.random()*GAMES.length)]', 'DEMO_GAMES[Math.floor(Math.random()*DEMO_GAMES.length)]')
rep('const tiles = c.ids.map(id=>byId[id]).filter(Boolean).map(tile).join("");',
    'const tiles = c.ids.map(id=>byId[id]).filter(Boolean).filter(g=>DEMO_ONLY.has(g.id)).map(tile).join(""); if(!tiles) return "";', 1)
rep('const surprise = `', 'const demonote = `<section class="catblock"><div class="cat-h"><span class="cat-n">Demo cut</span><span class="cat-t">%d of the twenty-seven games</span></div></section>`;\n  const surprise = `' % len(ids), 1)
assert 'blocks + surprise' in s or 'blocks+surprise' in s, 'grid join not found'
s = s.replace('blocks + surprise', 'blocks + demonote + surprise').replace('blocks+surprise', 'blocks+demonote+surprise')
rep('$("#gameGrid").onclick=', 'if(typeof S!=="undefined" && !DEMO_ONLY.has(S.game)){ S.game=DEMO_GAMES[0].id; }\n$("#gameGrid").onclick=', 1)
desc = "%d of Sparks' twenty-seven brain games, cut for the portfolio." % len(ids)
rep('Twenty-seven quick brain games — creativity, word links, patterns, rhyme, plus focus & memory trainers.', desc, 2)
DST.mkdir(parents=True, exist_ok=True)
for f in SRC.iterdir():
    if f.name == 'index.html': continue
    if f.is_dir(): shutil.copytree(f, DST/f.name, dirs_exist_ok=True)
    else: shutil.copy2(f, DST/f.name)
man = (DST/'manifest.webmanifest'); t = man.read_text(); man.write_text(t.replace('Twenty-seven quick brain games \\u2014 creativity, word links, patterns, rhyme, plus focus & memory trainers.', desc))
(DST/'index.html').write_text(s)
print('wrote', DST/'index.html', len(s), 'bytes; games:', ids)
