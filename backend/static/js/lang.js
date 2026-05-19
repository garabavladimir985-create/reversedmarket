function getLang(){
    return localStorage.getItem("lang") || "ru";
}

function setLang(lang){
    localStorage.setItem("lang", lang);
    applyLang();
}

function applyLang(){
    const lang = getLang();

    document.querySelectorAll("[data-ru][data-en]").forEach(el => {
        el.innerText = el.dataset[lang];
    });

    document.querySelectorAll("[data-placeholder-ru][data-placeholder-en]").forEach(el => {
        el.placeholder = lang === "ru"
            ? el.dataset.placeholderRu
            : el.dataset.placeholderEn;
    });

    const ruBtn = document.getElementById("ru-btn");
    const enBtn = document.getElementById("en-btn");

    if(ruBtn) ruBtn.classList.toggle("active", lang === "ru");
    if(enBtn) enBtn.classList.toggle("active", lang === "en");
}

document.addEventListener("DOMContentLoaded", applyLang);