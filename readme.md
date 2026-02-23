# very_useful_bot
下載最新版本 (不包含說明文件)：
[v1.9.2.2](https://github.com/d1fficult222/very_useful_bot/releases/latest) (2026/02/23 更新)  
[檢視更新紀錄](docs/changelog.md)  


VeryUsefulBot 是一個非常有用的Discord機器人，提供以下功能：

- ### 事件提醒
    建立提醒事項，不再忘記明天該做什麼

- ### Wordle
    在 Discord 上就能玩的 Wordle 小遊戲，一天可以玩無數次 

- ### C++ Online Judge (線上解題系統)
    一個在 Discord 上的 OJ 系統，目前只支援 C 和 C++

- ### 數學計算
    解決一些簡單數學，例如約分分數、行列式、向量的內外積等。

- ### 單字卡
    複習單字的小工具。



## 安裝說明
> 運行環境：Linux, macOS, Windows等   
> **需可執行bash，且可執行 `gcc` 和 `g++`，才可以使用OJ系統**  

以可執行bash的系統為例：
```bash
# 下載 VeryUsefulBot
git clone https://github.com/dfficult/very_useful_bot

# 安裝額外的 module
pip3 install discord                # Discord 模組
pip3 install pillow                 # 使用裡面的 PIL 模組用於 Wordle 繪製結果
pip3 install python-dotenv          # 使用 env 存取TOKEN

# 輸入 Token
cd very_useful_bot/dc_bot/          # 請在 dc_bot 目錄下運行
echo "TOKEN = MyToken" > token.txt  # 然後輸入你的 TOKEN

# 執行
python3 main.py
```

[更多說明](docs/tutorial.md)


## 所有指令說明 
> [!] 以下說明文件可能已經過時  

VeryUsefulBot 目前使用 app_commands 的斜線指令 (Slash Command)，之後將改用 hybrid_command，以增加前綴指令的支援。

### 遊戲
[`/wordle`](docs/wordle.md) `/slot`

### 工具
`/calculator` `/daysleft`

### 單字卡
[`/flashcard`](#單字卡)

### 隨機
[`/eat`](docs/eat.md/#eat) [`/dice`](docs/math.md/#dice-faces) [`/rand`](docs/math.md/#rand-items)


### 提醒
[`/note_list`](docs/notice.md/#note_list) [`/notice_after`](docs/notice.md/#notice_after) [`/notice_at`](docs/notice.md/#notice_at) [`/notice_delete`](docs/notice.md/#notice_delete) [`/sticky_note`](docs/notice.md/#sticky_note) 

### OJ
[`/code`](docs/vuboj.md/#顯示題目) [`/submit_code`](docs/vuboj.md/#提交程式碼)

### 數學
[`/average`](docs/math.md/#average) [`/c`](docs/math.md/#c) [`/common_deg_to_rad`](docs/math.md/#common_deg_to_rad) [`/correlation`](docs/math.md/#correlation) [`/det2`](docs/math.md/#det2) [`/det3`](docs/math.md/#det`) [`/factorize`](docs/math.md/#factorize) [`/invrmtx2`](docs/math.md/#invrmtx2) [`/p`](docs/math.md/#p) [`/simfrac`](docs/math.md/#simfrac) [`/solve21`](docs/math.md/#solve21) [`/solve31`](docs/math.md/#solve31) [`/surface`](docs/math.md/#surface) [`/vector`](docs/math.md/#vector) [`/vectorl`](docs/math.md/#vectorl) 


### 其他
[`/option`](docs/options.md) `/quotify` [`/load`](docs/tutorial.md/#載入卸載重載指令) [`/unload`](docs/tutorial.md/#載入卸載重載指令) [`/reload`](docs/tutorial.md/#載入卸載重載指令) [`/ping`](docs/tutorial.md/#測試)
