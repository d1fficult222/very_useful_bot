# Very Useful Bot C++ Online Judge System (VUBOJ)
這是一個簡易的線上解題系統 (Online Judge, OJ)，就是輸入程式碼，然後交由系統批改的平台。目前的程式語言僅支援C++，未來會再製作Python的版本。


VUBOJ目前不能：
- 顯示AC (Accepted) 比例
- 告訴你錯誤訊息，例如NA、WA、TLE等
- 使用除了 C/C++ 以外的語言
- 發生無限迴圈時可能無法自動停止

運行程式的限制為 (可以在後台修改)：
- 語言：C/C++
- 時間：<1s
- 記憶體限制：256MB


## 新增題目
[參考此說明：新增題目json檔案](oj_create.md)

新增檔案後，依照難易度將檔案放入 [`assets/code_test/0`](/dc_bot/assets/code_test/0/) 或 [`assets/code_test/1`](/dc_bot/assets/code_test/1/) 或 [`assets/code_test/2`](/dc_bot/assets/code_test/2/)  

檔案名稱請命名為編號，如 `1.json`, `2.json` 等  

`last_id.txt` 是用於顯示該難易度下最後的題號


## 顯示題目

使用 `/code` 指令顯示題目

## 提交程式碼

使用 `/submit_code`，輸入題號與使用的程式語言，將開啟輸入視窗，貼上你的程式碼後會開始執行測試並顯示結果。