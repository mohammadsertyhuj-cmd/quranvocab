[app]
title = Quran Vocab 9
package.name = quranvocab
package.domain = org.quran9
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
source.exclude_dirs = .github,.buildozer,bin,__pycache__
version = 1.0
icon.filename = %(source.dir)s/icon.png
requirements = python3,kivy==2.3.0,arabic-reshaper==3.0.0,python-bidi==0.4.2,six
orientation = portrait
fullscreen = 0

android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.allow_backup = True

p4a.branch = v2024.01.21
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0
