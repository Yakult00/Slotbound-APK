#!/usr/bin/env python3
"""把 love-android 的工程改成 SlotBound 的配置。

用法: python3 tools/patch_android_project.py <love-android 目录>

做四件事（与 love-actions-android 的行为一致，只是少了 debug 变体）：
  1. app/build.gradle 插入 release signingConfigs，并让 release buildType 用它
  2. AndroidManifest.xml 换图标、开 OpenGL ES 3.0
  3. gradle.properties 写入包名 / 版本 / 应用名
  4. 断言 keystore 已就位

签名密码只从环境变量读，不落盘、不打印。
"""
import os
import re
import sys

APP_NAME = "SlotBound"
BUNDLE_ID = "com.yakult00.slotbound"
ORIENTATION = "landscape"


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def patch_build_gradle(root):
    path = os.path.join(root, "app", "build.gradle")
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()

    if "signingConfigs" in data:
        print("build.gradle: signingConfigs 已存在，跳过")
        return

    # release buildType 里挂上签名
    pos = data.find("proguardFiles")
    if pos < 0:
        fail("build.gradle 里找不到 proguardFiles")
    pos = data.find("\n", pos) + 1
    data = data[:pos] + "            signingConfig signingConfigs.release\n" + data[pos:]

    # 在 buildTypes 之前插入 signingConfigs 块
    pos = data.find("buildTypes") - 4
    if pos < 4:
        fail("build.gradle 里找不到 buildTypes")
    block = (
        "    signingConfigs {\n"
        "        release {\n"
        "            storeFile file('./android.keystore')\n"
        "            keyAlias '%s'\n"
        "            keyPassword '%s'\n"
        "            storePassword '%s'\n"
        "        }\n"
        "    }\n"
    ) % (
        os.environ["KEY_ALIAS"],
        os.environ["KEY_PASS"],
        os.environ["STORE_PASS"],
    )
    data = data[:pos] + block + data[pos:]

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    print("build.gradle: 已插入 release 签名配置")


def patch_manifest(root):
    path = os.path.join(root, "app", "src", "main", "AndroidManifest.xml")
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    before = data
    data = data.replace("OpenGL ES 2.0", "OpenGL ES 3.0")
    data = data.replace("0x00020000", "0x00030000")
    data = data.replace("@drawable/love", "@drawable/icon")
    if data == before:
        fail("AndroidManifest.xml 没有任何替换命中（图标/GL 版本都还在）")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    print("AndroidManifest.xml: 图标 -> @drawable/icon, GL ES 3.0")


def write_gradle_properties(root):
    """只覆盖必须改的键，其余（注释、默认项）原样保留。

    game.love 有 100MB，:app:compressEmbedRecordReleaseAssets 默认 512MB 堆会
    直接 Java heap space 崩掉，所以必须显式给 gradle 加大堆。
    """
    version_name = os.environ["VERSION_STRING"]
    version_code = os.environ["VERSION_CODE"]
    if not re.fullmatch(r"\d+", version_code):
        fail("VERSION_CODE 不是纯数字: %r" % version_code)
    name_bytes = ",".join(str(b) for b in APP_NAME.encode("utf-8"))

    wanted = {
        "app.name_byte_array": name_bytes,
        "app.application_id": BUNDLE_ID,
        "app.orientation": ORIENTATION,
        "app.version_code": version_code,
        "app.version_name": version_name,
        "android.enableJetifier": "false",
        "android.useAndroidX": "true",
        "android.defaults.buildfeatures.buildconfig": "true",
        "android.nonTransitiveRClass": "true",
        "android.nonFinalResIds": "true",
        "org.gradle.caching": "true",
        "org.gradle.jvmargs": "-Xmx6g -XX:MaxMetaspaceSize=1g -Dfile.encoding=UTF-8",
    }

    path = os.path.join(root, "gradle.properties")
    kept = []
    seen = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                m = re.match(r"\s*([A-Za-z0-9_.-]+)\s*=", line)
                if m and m.group(1) in wanted:
                    if m.group(1) not in seen:
                        kept.append("%s=%s" % (m.group(1), wanted[m.group(1)]))
                        seen.add(m.group(1))
                    continue
                kept.append(line)
    for key, value in wanted.items():
        if key not in seen:
            kept.append("%s=%s" % (key, value))

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(kept).rstrip("\n") + "\n")
    print("gradle.properties: version=%s (%s), jvmargs=%s" % (version_name, version_code, wanted["org.gradle.jvmargs"]))


def main():
    if len(sys.argv) != 2:
        fail("用法: patch_android_project.py <love-android 目录>")
    root = sys.argv[1]
    for key in ("KEY_ALIAS", "KEY_PASS", "STORE_PASS", "VERSION_STRING", "VERSION_CODE"):
        if not os.environ.get(key):
            fail("环境变量 %s 为空（secrets 没配或传递失败）" % key)

    patch_build_gradle(root)
    patch_manifest(root)
    write_gradle_properties(root)

    if not os.path.exists(os.path.join(root, "app", "android.keystore")):
        fail("app/android.keystore 不存在")
    print("OK: 工程已按 SlotBound 配置完成")


if __name__ == "__main__":
    main()
