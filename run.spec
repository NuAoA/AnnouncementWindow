# -*- mode: python -*-
import shutil, os

block_cipher = None

a = Analysis(['run.py'],
             pathex=['D:\\workspace\\Announcement Window\\AnnouncementWindow'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='AnnouncementWindow',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon='Data\\favicon.ico',
          )

os.makedirs('dist/Data')
shutil.copyfile('Data/favicon.ico', 'dist/Data/favicon.ico')
shutil.copyfile('filters.txt', 'dist/filters.txt')
shutil.copyfile('Data/filters.dat', 'dist/Data/filters.dat')
shutil.copyfile('readme.md', 'dist/readme.md')
