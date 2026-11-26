# 版权与许可范围

## 本仓库的脚本与文档

`LICENSE` 里的 MIT 许可覆盖本仓库的构建脚本、工具、补丁和文档，即：

- `.github/`（编译流水线、issue 模板）
- `tools/`（打包脚本、哈希 pin）
- `patches/`（love-android 工程补丁）
- `android/`（图标等外壳资源）
- 根目录的 Markdown 文档

## 游戏本体

`game.love`（包括发布在 release 资产 `game-latest` 里的那份）及其中的美术、音频、数据、
代码，版权归原作者 **Optima Arch** 所有，**不在 MIT 许可范围内**，本仓库不授予任何
使用、复制或再分发许可。

本仓库不存放游戏本体源码，只在构建时按 `tools/game_love.sha256` 校验哈希后原样打包，
也未对游戏做商业性使用。请通过正规渠道支持正版原作。

## 引擎

打包用的 LÖVE 11.5 及 love-android 遵循其各自的许可（zlib / Apache-2.0），未做修改分发，
仅在构建期从上游源码编译。
