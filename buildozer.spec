[app]
title = DARKSTREAK
package.name = darkstreak
package.domain = org.darkstreak
source.dir = .
source.include_exts = py,kv,json,png,jpg
version = 0.1
requirements = python3==3.12.10,kivy==2.3.1
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.branch = master
