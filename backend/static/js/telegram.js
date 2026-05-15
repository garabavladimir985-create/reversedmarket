const tg = window.Telegram?.WebApp;

if(tg){
    tg.expand();

    const user = tg.initDataUnsafe?.user;

    if(user){
        localStorage.setItem("telegram_user", JSON.stringify(user));

        fetch("/api/telegram-register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(user)
        })
        .then(res => res.json())
        .then(data => {
            localStorage.setItem("registered_user", JSON.stringify(data.user));
            console.log("Telegram user registered", data.user);
        })
        .catch(err => console.log("Telegram register error", err));
    }
}

function getTelegramUser(){
    return JSON.parse(localStorage.getItem("telegram_user")) || null;
}

function getRegisteredUser(){
    return JSON.parse(localStorage.getItem("registered_user")) || null;
}

function openTelegramProfile(){
    let user = getTelegramUser();

    if(user){
        window.location.href = "/profile?telegram_id=" + user.id;
    }else{
        window.location.href = "/profile";
    }
}