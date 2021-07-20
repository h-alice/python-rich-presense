# Python Discord Presence
自訂自己的遊戲狀態欄!  
![presence](https://i.imgur.com/x9QfVgN.png)  
Icon Credit: NatLee

## 需求 Requirements 
Python 3.8+  
[Get Python](https://www.python.org/downloads/)

## 前置作業 Prepare  

### 建立App
在Discord Developer Portal建立自己的App.  
注意: 這裡的NAME日後就會顯示在狀態欄(建立之後可以更改)  
![create app](https://i.imgur.com/97ddiFH.png)

### 取得Application ID
建立App之後, 在General Information可以看到Application ID.  
筆記起來, 這個之後會用到.  
![app id](https://i.imgur.com/GvNG1Rc.png)

### (Optional)上傳素材
如果需要顯示自己的Icon, 需要先上傳素材到Discord.  
在 Rich Presence -> Art Asset 可以上傳素材.  
上傳後旁邊的英文字是代表這張圖的Key, 這個之後會用到.
![assert](https://i.imgur.com/Cqz8qw5.png)

## Activity JSON 格式
欄位名稱對應的顯示位置可以參考官方圖.  
詳細一點的說明寫在最底下.  
![activity](https://discord.com/assets/43bef54c8aee2bc0fd1c717d5f8ae28a.png)

## 執行啦!
打開一個終端(Windows鍵+R 然後打cmd).
```
cd <ipc.py跟activity.json的位置>
python ./ipc.py <前面筆記的App ID> <Activity.json 檔案名稱>
```
沒有出錯的話就會改寫狀態了. 應該是不會出錯吧, 大概...  
Ctrl+C就能結束了

## 小說明&注意事項  

### 上傳素材當顯示ICON 
```json
"assets": {
    "large_image": "<上傳素材的Key>",
    "large_text": "YOOOOO",
    "small_image": "<上傳素材的Key>",
    "small_text": "REEEEE"
}
```
large_image 是Icon本體, 前面步驟上傳素材的Key.  
large_text 是滑鼠在Icon上面顯示的文字.  
small_image 是Icon右下的小圈圈, 一樣是前面步驟上傳素材的Key.  
small_text 是滑鼠在小圈圈上面顯示的文字.  
  
### 加個按鈕  
```json
"buttons": [
    {"label": "<按鈕的名字>", "url": "<按下按鈕要開的網頁>"}
]
```

## 乾 還真的遇到問題喔?
Discord: halice#1142  





