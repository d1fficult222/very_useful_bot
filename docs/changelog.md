# ChangeLog

### v1.8 2025六七八月更新
- [1.8.4](https://github.com/d1fficult222/very_useful_bot/releases/tag/v1.8.2) (2025.9.11)
    - 修改：更新了所有指令說明
    - 修復：`cmd.notice_at.hour`, `cmd.notice_at.minute`, `cmd.solve21.description`, `cmd.solve31.description`
    - 修復：以 UTF-8 開啟語言檔案
- [1.8.3](https://github.com/d1fficult222/very_useful_bot/releases/tag/v1.8.2) (2025.8.7)
    - 修改：`load`, `unload`, `reload` 指令需要管理員密碼
- [1.8.2](https://github.com/d1fficult222/very_useful_bot/releases/tag/v1.8.2) (2025.7.17)
    - 新增：`load`, `unload`, `reload` 指令，方便管理Cog指令
    - 新增：`ping` 指令，查看延遲
    - 修改：把 token.txt 改成 .env，增加安全性
    - 修改：Quotify的圖片名稱改為 `quotify.png`
- [1.8.1](https://github.com/d1fficult222/very_useful_bot/releases/tag/v1.8.1) (2025.6.10)
    - 新增：開發 VeryUsefulBot 的教學 (部分)
    - 更改：可以從 `settings.py` 修改 Bot Activity 的類型，不用到 `main.py` 修改
    - 更改：將cog檔案的載入顯示訊息由**指令模組(command modules)**改為**程式套件(packages)**
    - 修復：指令現在會同步到客戶端，部分更名的指令可以使用
    - 修復：Quotify 的作者修正為訊息的作者，非使用指令的作者
    - 修復：Quotify 可以讀取 Embed 裡的內容
    - 修復：`menu.quotify` 原沒有對應的顯示文字，現在加上，名為**Quotify**
- [1.8.0](https://github.com/d1fficult222/very_useful_bot/releases/tag/v1.8.0) (2025.5.31)
    - 新增： `Quotify` : 將一段話做成引文圖片
    - 新增：英文語言檔案 
    - 更改：此版本使用Cog架構重新編寫程式架構  
    - 更改：將 `calculator`, `daysleft`, `wordcount` 整合至 `tools.py`
    - 更改：重新編寫架構同時，移除以下指令: `addfood`, `help`
    - 更改：重新命名 `expense.py` -> `money_track.py`
    - 更改：Wordle程式中的陣列排序以及大小寫切換改用Python內建，以改進效能
    - 更改：將 `changlog` 從 `readme.md` 中獨立出來
    - 移除： `.vscode` 自訂輸入
    - 移除：計算機黑名單
    - 移除： `my_address` 彩蛋 (1.7.1) ( `hello world` 彩蛋仍保留)


### v1.7 2025五月更新
- [1.7.2](https://github.com/d1fficult222/very_useful_bot/commit/690776a64e3a1626e403e800213d740e314c85c4) (2025.5.8)
    Added Slot Machine
    - 新增：Slot Machine
- [1.7.1](https://github.com/d1fficult222/very_useful_bot/commit/00c1d9cba497b517cf1feb8ba8ef59868bf5f974) (2025.4.25)
    Added history to Expense Tracking System, New easter egg, Fixed Wordle Missing Record
    - 新增：記帳系統可以查看紀錄 (最近20筆)
    - 新增：一個彩蛋
    - 修復：Wordle 修復紀錄重置問題
- [1.7.0.02](https://github.com/d1fficult222/very_useful_bot/commit/61ddf75cf6abfefde6802f8673843e8e07e79efa) (2025.4.14)
    Fixed common_deg_to_rad bug, Updated Readme.md
    - 修復： `common_deg_to_rad`的錯誤
- [1.7.0.01](https://github.com/d1fficult222/very_useful_bot/commit/a60013b8a61c26aa785df2b15287c331e3bce235) (2025.4.5)
    Fixed Wordle Fatal Bug, Updated Readme.md
    - 修復：Wordle的錯誤
- [1.7.0](https://github.com/d1fficult222/very_useful_bot/commit/dcff8de13117bb927f6a0a1edba376a4f5115d81) (2025.4.5) Multi-Language Support, Expense Tracking System, Right Click Menu, Wordle Send Fix, New Math Command, User Option
    - 新增：記帳系統
    - 新增：語言檔案
    - 新增：右鍵選單
    - 新增：`common_deg_to_rad` 
    - 新增：`user_options`
    - 更改：`dice` 可以決定一次投擲幾顆 
    - 更改：`surface` 結果自動化簡
    - 更改：重新命名 `note` -> `sticky_notes`
    - 修復：`notice`不能輸入0分
    - 修復：`det2`, `det3`, `invrmtx` 對齊
### v1.6 OJ and Notice (Again)
- [1.6.0](https://github.com/d1fficult222/very_useful_bot/commit/c3912645dc450a1694cf162abf68971de95962ff) Fixed oj compile error, removed new_code_q/today/mlend/mdelete/mhistory commands, redesigned code, added sticky notes, made embed colors environmental variables
- [1.6 Beta 3](https://github.com/d1fficult222/very_useful_bot/commit/2e903e3d92a82bbf0bd582de5f3acf775ccaf59d) Updated notice system, Minor fixes to wordle.py and eat.py
- [1.6 Beta 2.1](https://github.com/d1fficult222/very_useful_bot/commit/10ea36ca48434768c5f14187c06a35c87bdb936e) Updated `readme.md`
- [1.6 Beta 2](https://github.com/d1fficult222/very_useful_bot/commit/00674c1d709546fe6cf40146b8e106ede515b8ff) Wordle: Added stats to wordle, Edit message by getting message instead of interaction.edit_original_response
- [1.6 Beta 1.1](https://github.com/d1fficult222/very_useful_bot/commit/8847221d368e1cc555501f00d18972904e464c02) Removed `runcode.sh`
- [1.6 Beta 1](https://github.com/d1fficult222/very_useful_bot/commit/0b451bfbc8d80d88682abdf2cc80a6255d0e7c29) Token is now a seperate file, Reorganized all the files (Put data in `assets` folder, renamed `codes.py` to `oj.py`)

### v1.5 FlashCard, Wordle, and Calculator
- [1.5.3.01](https://github.com/d1fficult222/very_useful_bot/commit/ebe4429aee3f8b719e3b20cbeb88e701b7b62a43) Wordle: Fixed sometimes it does not show image properly
- [1.5.3](https://github.com/d1fficult222/very_useful_bot/commit/21a99691a45973f0b107d16f751268cd2f1f1ce4) Wordle: Edit message instead of creating a new message on every guess, Debug Mode set to ephemeral, Changed some variable to constant, Deletes message after 2 seconds, Added allowed guesses list
- [1.5.2.02](https://github.com/d1fficult222/very_useful_bot/commit/1d2e5f2fe09f9ac37c191c8a4fe95f5ec3d55d16) Fixed incorrect bottom color showing, made better debug mode, updated [readme.md](#very_useful_bot), added changelog
- [1.5.2.01](https://github.com/d1fficult222/very_useful_bot/commit/251297706200472cac2c86b7f59cd9faca392d73) Fixed winnig at 6th attempt returned lose
- [1.5.2](https://github.com/d1fficult222/very_useful_bot/commit/f637fd0beaff57ef169b897cebe626f3e623d7ba) Added Wordle
- [1.5.1](https://github.com/d1fficult222/very_useful_bot/commit/2c266c7dbe273a4024ec436c6f4166b30ca15cd6) Added Calculator
- [1.5.0.01](https://github.com/d1fficult222/very_useful_bot/commit/4c0967b52e9b8db868673ae6008c1ee8d64f0456) Updated readme.md (Forgot)
- [1.5.0](https://github.com/d1fficult222/very_useful_bot/commit/3cefe82fe8de5bd4ddfbd8f399121f33c0fe90e0) Added Flashcard, started adding version properly

### v1.4 OJ Update
- [1.4.3](https://github.com/d1fficult222/very_useful_bot/commit/4afcf33c5d91dc77e4d2224b04974a1692899f78) Fixed '\n' and ' ' evaluation of the code output
- [1.4.2](https://github.com/d1fficult222/very_useful_bot/commit/2c06455b2d24384ea21aa4472793c95199beed7d) Fixed file reading
- [1.4.1.01](https://github.com/d1fficult222/very_useful_bot/commit/4d6215d7050412a53413f10570a5ef1cbfac91e3) Fixed oj_create.md
- [1.4.1](https://github.com/d1fficult222/very_useful_bot/commit/25a511afea089d79ba3e2103b160afe8918a0a1e) Removed one difficulty as it causes confusion, fixed missing last_id
- [1.4.0](https://github.com/d1fficult222/very_useful_bot/commit/bfc110815fe3ae92b06328262ed4fe301ce2aac9) Added difficulty, added new code adding support

### v1.3 Eat Command Update
- [1.3.1](https://github.com/d1fficult222/very_useful_bot/commit/88184e013a0a7c9e560f802bbd3d05b9590b1ced) Correct File location
- [1.3.02](https://github.com/d1fficult222/very_useful_bot/commit/d222ad4f90e52aa012505687a04ae7b51c0c1ed0) Removed wrong file
- [1.3.01](https://github.com/d1fficult222/very_useful_bot/commit/ee4710d136803f2c6a9df2153f0519588816ae2f) Removed wrong file
- [1.3.0](https://github.com/d1fficult222/very_useful_bot/commit/5289ac19a157eb6867fb0887963b92e6b86d6478) Fixed bot.change_presence not working, 
updated /eat by adding amount so you don't have to type the command 30 times

### v1.2 OJ and Notice
- [1.2](https://github.com/d1fficult222/very_useful_bot/commit/4608b547e9dd04fb66aa9e74a523c95d7570c00a) Added OJ and Notice, removed `__pychche__`, removed yazy game

### v1.1 Some Commands Update

- [1.1.2](https://github.com/d1fficult222/very_useful_bot/commit/46ff362da81c198268b4db6defacbdab017cb199) Added solve31, solve21, factorial commands

- [1.1.1](https://github.com/d1fficult222/very_useful_bot/commit/dade39e5ea98ed2254146d5044f303392aa9f37e) Removed drop down menu test file

- [1.1.0](https://github.com/d1fficult222/very_useful_bot/commit/0c3f8782435a7c9118399b1b6c6a8a254f56eada) Added today and vectorl command

### v1.0 Initial Commit
- [1.1](https://github.com/d1fficult222/very_useful_bot/commit/fd4d1b2cea2580cf75ce1eb9576a25a0e0b01ef0) Removed README.md generated by GitHub because my [readme.md](#very_useful_bot) exists
- [v1](https://github.com/d1fficult222/very_useful_bot/commit/58cbbdc727c8fb132622094c79042119ebf32742#diff-5a831ea67cf5cf8703b0de46901ab25bd191f56b320053be9332d9a3b0d01d15) Added pretty much everything to [GitHub](https://github.com/d1fficult222/very_useful_bot)
- [v0](https://github.com/d1fficult222/very_useful_bot/commit/853c6eb2668d09d40497a7cfc83d37ae593354f5) Initial Commit