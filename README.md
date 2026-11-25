# SlotBound 安卓版

SlotBound（LÖVE 11.5）在安卓上的单体 APK：游戏直接嵌进包里，装上就能玩，不用另外装播放器、不用另外放 game.love。

- 包名：`com.yakult00.slotbound`，应用名 SlotBound，纯横屏
- 构建：GitHub Actions（`.github/workflows/android.yml`），手动触发，产物是 debug APK（`SlotBound.apk`），只出 workflow artifact，不发 Release
- 游戏内容来自 [Yakult00/Slotbound-iOS](https://github.com/Yakult00/Slotbound-iOS)（CI 里直接 checkout 打包），版本号跟 iOS 走；训练器面板暂无，iOS 的面板是 ObjC dylib，安卓上不能用，`trainer_backend.lua` 在包里但没面板写指令，默认关闭，无影响
- 测试机：OnePlus 9RT

## 构建

Actions 页 → Build Android APK → Run workflow（version 留空用 iOS 最新 tag，不填也行）。
