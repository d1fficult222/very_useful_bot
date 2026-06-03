# very_useful_bot

VeryUsefulBot 是一個非常有用的 Discord 機器人，可以管理行事曆、建立提醒、遊玩小遊戲、還有一個 C++ Online Judge 系統！

下載: [v1.10](https://github.com/d1fficult222/very_useful_bot/releases/latest)  
[Changelog](docs/changelog.md)  
[安裝說明](#安裝說明)


- ### 行事曆與事件提醒
    建立提醒事項，不再忘記明天該做什麼  
    [行事曆說明]()

- ### Wordle
    在 Discord 上就能玩的 Wordle 小遊戲，一天可以玩無數次  
    [Wordle 遊戲說明](docs/wordle.md)   

- ### C++ Online Judge (線上解題系統)
    一個在 Discord 上的 OJ 系統，目前只支援 C 和 C++  
    [OJ 說明](docs/vuboj.md)  
    [建立 OJ 題目](docs/oj_create.md)  

- ### 單字卡
    複習單字的小工具。  



## 安裝說明
下載 VeryUsefulBot
```bash
git clone https://github.com/dfficult/very_useful_bot
cd very_useful_bot

# 輸入 Token (Required)
echo "TOKEN = <MyToken>" >> .env

# 建立管理員密碼 (Optional, 用於 load/unload/restart 指令)
echo "PASSWORD = <MyPassword>" >> .env

# 輸入你的 email (Optional, 用於 OSRM API)
echo "EMAIL = <MyEmail@something.com>" >> .env
```
方法一：測試環境
```bash
# 建立 venv
python3 -m venv .venv
source .venv/bin/activate

# 安裝額外的 module
pip install -r requirements.txt

# 安裝繁體中文字型，用於圖片文字繪製 (Wordle, Quotify)
sudo apt install fonts-noto-cjk

# 執行
python3 main.py
```
方法二：使用 Docker
```bash
# 已寫好 dockerfile，直接執行
sudo docker compose up -d --build
```