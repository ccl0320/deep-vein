# ⛏ 深坑淘金 Deep Vein

3D 線上多人隱藏身分挖礦遊戲。開一個房間、設好密碼，就能和朋友用電腦或手機一起玩。

**▶ 開始玩：https://ccl0320.github.io/deep-vein/**

玩法機制致敬經典桌遊《矮人礦坑》。美術、3D 模型、音效和程式碼都是原創。

## 玩法

- 4 名礦工各抽一張身分卡：**淘金者**或**搗蛋鬼**（5 張身分卡只發 4 張，所以有時候根本沒有搗蛋鬼）。
- 淘金者要從起點挖出一條連續通道，通到 3 張終點卡中藏著金脈的那一張。
- 搗蛋鬼要暗中阻撓：放死路、弄壞別人的工具、引爆落石。
- 地圖卡可以偷看終點卡；工具壞了就不能挖通道，要等人幫你修。

## 線上對戰

1. 輸入暱稱 → **建立房間**（房號可以自訂，密碼可以留空）。
2. 把房號和密碼告訴朋友，或按「複製邀請連結」傳給他們。
3. 朋友選 **加入房間** → 輸入房號和密碼。
4. 房主按「開始遊戲」，空位由 AI 補上。

技術說明：

- 連線使用 [PeerJS](https://peerjs.com/) 的 WebRTC 點對點連線，沒有後端，也不用註冊帳號。
- 由房主的瀏覽器負責跑遊戲，所以遊戲進行中房主要保持頁面開啟。
- 其他玩家只會收到公開資訊和自己的手牌、身分、偷看結果，看不到別人的牌或金脈位置。
- 有玩家斷線時，他的座位會暫時交給 AI 代打。用同樣的暱稱重新加入，就能接回原本的座位。
- 少數公司或校園網路會擋點對點連線，連不上的話可以改用手機熱點。

## 專案結構

```
index.html                    遊戲本體（Three.js + 遊戲引擎 + 網路 + 音效）
assets/deepvein_assets.glb    Blender 產生的 3D 模型
assets/the_glass_orchard.mp3  背景音樂
tools/deepvein_assets.py      產生 GLB 的 Blender 腳本
```

重新產生模型：

```bash
blender -b -P tools/deepvein_assets.py -- assets/deepvein_assets.glb
# 或者用 pip 版 bpy：python tools/deepvein_assets.py assets/deepvein_assets.glb
```

本機測試：`python3 -m http.server`，再打開 http://localhost:8000
