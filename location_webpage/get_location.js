const urlParams = new URLSearchParams(window.location.search);
const guildID = urlParams.get('guildID');
const channelID = urlParams.get('channelID');
const token = urlParams.get('token');

const BACKEND_URL = '/location';

document.getElementById('locate-btn').addEventListener('click', () => {
    getLocation();
});

function getLocation() {
    if (!token) {
        alert("此定位連結無效或已過期");
        window.close();
        return;
    }

    if (!navigator.geolocation) {
        alert("你的瀏覽器不支援定位");
        window.close();
        return;
    }

    document.getElementById('status').innerText = '正在取得位置，請稍後...';

    navigator.geolocation.getCurrentPosition(success, error, {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    });
}



function success(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    document.getElementById('status').innerText = "已取得位置，正在傳送至 Discord...";

    fetch(BACKEND_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token,
            latitude: latitude,
            longitude: longitude
        })
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('status').innerText = "位置傳送成功";
            if (guildID && channelID) {
                window.location.href = `discord://app/channels/${guildID}/${channelID}`;
            }
        } else {
            switch(response.status) {
                case 400:
                    alert("伺服器沒有收到正確的數值，請再試一次 (400)");
                    break;
                case 403:
                    alert("連結可能無效，請從 Discord 重新生成取得位置按鈕 (403)");
                    break;
                case 404:
                    alert("找不到伺服器，請聯絡維護人員 (404)");
                    break;
                case 500:
                    alert("伺服器發生了錯誤，請聯絡維護人員 (500)");
                    break;
                default:
                    alert(`伺服器回應錯誤，請聯絡維護人員 (${response.status})`);
            }
        }
    })
    .catch(err => {
        console.error(err);
        alert("連線到伺服器失敗");
    });
}

function error() {
    alert("無法取得你的位置，請確認是否開啟定位權限");
}


getLocation();