[< 返回 readme.md](../readme.md)

# 架設 VeryUsefulBot
VeryUsefulBot 是一款使用 Python 開發的 Discord 機器人，使用 discord.py, pillow 等多個 Python 模組。本說明文件將簡單介紹如何自行架設 VeryUsefulBot。

### 目錄

## 下載與使用
1. 下載 VeryUsefulBot  
```bash
git clone https://github.com/d1fficult222/very_useful_bot
```
2. 進入 VeryUsefulBot 資料夾  
```bash
cd very_useful_bot
```
3. 輸入 TOKEN  
到 [Discord Developer Portal / My Applications](https://discord.com/developers/applications)，點選你的機器人應用程式，在左側選單中進入 Bot 頁面，點選 Reset Token 按鈕後會顯示新的 Token。  
```bash
echo "TOKEN = <MyToken>" >> .env
```
