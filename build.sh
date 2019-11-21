#!/bin/bash

sudo docker run --volume "$HOME/.buildozer":/home/user/.buildozer --volume "$PWD":/home/user/hostcwd kivy/buildozer -v android debug deploy \
&& adb devices \
&& adb uninstall org.test.mc \
&& adb install bin/mc-0.1-debug.apk \
&& adb shell am start -n org.test.mc/org.kivy.android.PythonActivity