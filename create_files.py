import os

os.makedirs(".github/workflows", exist_ok=True)

# 1. project.godot
with open("project.godot", "w", encoding="utf-8") as f:
    f.write("""[application]
config/name="مرکز منابع یادگیری - آموزش واقعیت مجازی"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.3", "Forward Plus")

[xr]
openxr/enabled=true
xr_features/xr_coding=true
""")

# 2. export_presets.cfg
with open("export_presets.cfg", "w", encoding="utf-8") as f:
    f.write("""[preset.0]
name="Quest Android"
platform="Android"
runnable=true
advanced_options=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="build/cabinet-workshop.apk"

[preset.0.options]
architectures/arm64=true
architectures/armv7=false
package/unique_name="com.nioc.vr.learningcenter"
package/app_name="آموزش VR پالایش نفت"
vulkan/high_end_graphics=true
xr_features/openxr=true
""")

# 3. main.tscn
with open("main.tscn", "w", encoding="utf-8") as f:
    f.write("""[gd_scene load_steps=3 format=3]

[node name="MainScene" type="Node3D"]

[node name="XROrigin3D" type="XROrigin3D" parent="."]

[node name="XRCamera3D" type="XRCamera3D" parent="XROrigin3D"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.7, 0)

[node name="LeftController" type="XRController3D" parent="XROrigin3D"]
tracker = &"left_hand"

[node name="RightController" type="XRController3D" parent="XROrigin3D"]
tracker = &"right_hand"

[node name="Environment" type="Node3D" parent="."]

[node name="Floor" type="CSGBox3D" parent="Environment"]
size = Vector3(10, 0.1, 10)

[node name="WallLogoAndTitle" type="Label3D" parent="Environment"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2.5, -4)
text = "اداره آموزش و تعالی منابع انسانی
شرکت پالایش نفت اصفهان
مرکز منابع یادگیری"
font_size = 48

[node name="TrainingTable" type="CSGBox3D" parent="Environment"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.8, -1.5)
size = Vector3(1.5, 0.1, 0.8)
""")

# 4. workflow yml
with open(".github/workflows/build-apk.yml", "w", encoding="utf-8") as f:
    f.write("""name: Build Quest 2 APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
      - name: چک‌اوت پروژه
        uses: actions/checkout@v4
      - name: نصب جاوا ۱۷
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - name: ساخت debug keystore
        run: |
          mkdir -p ~/.android
          keytool -genkeypair -alias androiddebugkey -keypass android -keystore ~/.android/debug.keystore -storepass android -dname "CN=Android Debug,O=Android,C=US" -validity 9999 -keyalg RSA -keysize 2048
      - name: دانلود اجرایی گودو
        run: |
          wget -q "https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_linux.x86_64.zip" -O godot.zip
          unzip -q godot.zip && chmod +x Godot_v4.3-stable_linux.x86_64 && sudo mv Godot_v4.3-stable_linux.x86_64 /usr/local/bin/godot4
      - name: دانلود export templates
        run: |
          wget -q "https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_export_templates.tpz" -O templates.tpz
          mkdir -p "$HOME/.local/share/godot/export_templates/4.3.stable"
          unzip -q templates.tpz -d /tmp/templates_extract
          cp -r /tmp/templates_extract/templates/* "$HOME/.local/share/godot/export_templates/4.3.stable/"
      - name: نصب افزونه OpenXR Vendors
        run: |
          wget -q "https://github.com/GodotVR/godot_openxr_vendors/releases/download/3.1.2-stable/godotopenxrvendorsaddon.zip" -O openxr_vendors.zip
          mkdir -p addons
          unzip -q openxr_vendors.zip "asset/addons/godotopenxrvendors/*" -d /tmp/vendors_extract
          cp -r /tmp/vendors_extract/asset/addons/godotopenxrvendors addons/godotopenxrvendors
      - name: نصب Android Build Template
        run: |
          mkdir -p android
          unzip -q "$HOME/.local/share/godot/export_templates/4.3.stable/android_source.zip" -d android/build
          chmod +x android/build/gradlew
          echo "4.3.stable" > android/.build_version
      - name: ایمپورت اولیه
        run: godot4 --headless --editor --quit --path .
      - name: Export به APK
        env:
          GODOT_ANDROID_KEYSTORE_DEBUG_PATH: /home/runner/.android/debug.keystore
          GODOT_ANDROID_KEYSTORE_DEBUG_USER: androiddebugkey
          GODOT_ANDROID_KEYSTORE_DEBUG_PASSWORD: android
        run: |
          mkdir -p build
          godot4 --headless --verbose --export-debug "Quest Android" build/cabinet-workshop.apk
      - name: آپلود APK
        uses: actions/upload-artifact@v4
        with:
          name: cabinet-workshop-quest2-apk
          path: build/*.apk
          if-no-files-found: error
""")

print("تمامی فایل‌ها با موفقیت و بدون خطا ساخته شدند!")