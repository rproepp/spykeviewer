# -*- mode: python -*-

import os
import sys

import spykeviewer
import guidata
import guiqwt
import spyderlib

path = os.path.dirname(os.path.dirname(spykeviewer.__file__))

def dir_files(path, rel):
    ret = []
    for p,d,f in os.walk(path):
        relpath = p.replace(path, '')[1:]
        for fname in f:
            ret.append((os.path.join(rel, relpath, fname), os.path.join(p, fname), 'DATA'))
    return ret

a = Analysis([os.path.join(path, 'bin', 'freeze', 'dependencies.py'), os.path.join(path, 'bin', 'spykeview.py')],
             #pathex=[''],
             hiddenimports=[],
             hookspath=None,
             excludes='Tkinter')
#for s in a.scripts: # Remove useless dependencies script
#    if s[0] == 'dependencies':
#        a.scripts.remove(s)
#        break

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\main', 'main.exe'),
          debug=False,
          strip=None,
          upx=False,
          console=False)

a.datas.extend(dir_files(os.path.join(os.path.dirname(guidata.__file__), 'images'),
    os.path.join('guidata', 'images')))
a.datas.extend(dir_files(os.path.join(os.path.dirname(guiqwt.__file__), 'images'),
    os.path.join('guiqwt', 'images')))
a.datas.extend(dir_files(os.path.join(os.path.dirname(spyderlib.__file__), 'images'),
    os.path.join('spyderlib', 'images')))
a.datas.extend(dir_files(os.path.join(path, 'plugins'), 'plugins'))
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'main'))
