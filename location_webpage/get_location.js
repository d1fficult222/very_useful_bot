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
                window.location.href = `https://discord.com/channels/${guildID}/${channelID}`;
            }
        } else {
            alert("傳送失敗，伺服器回應錯誤");
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