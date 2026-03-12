# very_useful_bot

VeryUsefulBot 是一個非常有用的 Discord 機器人，可以管理行事曆、建立提醒、遊玩小遊戲、還有一個 C++ Online Judge 系統！

Latest Release: [v1.10](https://github.com/d1fficult222/very_useful_bot/releases/latest) (Updated 2026/3)  
[Changelog](docs/changelog.md)  


VeryUsefulBot 有以下功能：

> 說明檔案已過時，之後將更新

- ### 行事曆與事件提醒
    建立提醒事項，不再忘記明天該做什麼
    [行事曆說明]() (之後補上)
    [事件提醒說明 (即將移除)](docs/notice.md)
    [課表系統說明 (即將移除)](vub_timetable_tools/README.md)

- ### Wordle
    在 Discord 上就能玩的 Wordle 小遊戲，一天可以玩無數次 
    [Wordle 遊戲說明](docs/wordle.md) 

- ### C++ Online Judge (線上解題系統)
    一個在 Discord 上的 OJ 系統，目前只支援 C 和 C++
    [OJ 說明](docs/vuboj.md)
    [建立 OJ 題目](docs/oj_create.md)

- ### 數學計算
    解決一些簡單數學，例如約分分數、行列式、向量的內外積等。
    > 本功能即將移除。
    [數學計算說明 (即將移除)](docs/math.md)

- ### 單字卡
    複習單字的小工具。
    [單字卡說明]() (之後補上)



## 安裝說明
> 運行環境：Linux, macOS, Windows等   
> **需可執行bash，且可執行 `gcc` 和 `g++`，才可以使用OJ系統**  

以可執行bash的系統為例：
```bash
# 下載 VeryUsefulBot
git clone https://github.com/dfficult/very_useful_bot

# 安裝額外的 module
pip install -r requirements.txt

# 輸入 Token (Required)，以及建立管理員密碼 (Optional)
cd very_useful_bot
echo "TOKEN = <MyToken>" > token.txt
echo "PASSWORD = <MyPassword>" > token.txt

# 執行
python3 main.py
```

[更多說明](docs/tutorial.md)