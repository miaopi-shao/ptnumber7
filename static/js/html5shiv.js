//  檔案名稱:html5shiv.js 舊版IE兼容檔
function getIEVersion() {
    var ua = window.navigator.userAgent;
    var msie = ua.indexOf('MSIE '); // 判斷 MSIE 的版本字串
    if (msie > 0) {
        return parseInt(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
    }
    return false; // 不是 IE 瀏覽器
}

var ieVersion = getIEVersion();

if (ieVersion === 8) {
    // IE8 的處理：動態插入升級提示
    var warningDiv = document.createElement("div");
    warningDiv.style.clear = "both";
    warningDiv.style.textAlign = "center";
    warningDiv.style.position = "relative";

    var warningLink = document.createElement("a");
    warningLink.href = "http://windows.microsoft.com/en-US/internet-explorer/products/ie/home?ocid=ie6_countdown_bannercode";

    var warningImg = document.createElement("img");
    warningImg.src = "{{ url_for('static', filename='images/preloader.gif') }}";
    warningImg.border = "0";
    warningImg.height = "42";
    warningImg.width = "820";
    warningImg.alt = "Upgrade your browser";

    warningLink.appendChild(warningImg);
    warningDiv.appendChild(warningLink);

    document.body.appendChild(warningDiv); // 將提示插入頁面中
} else if (ieVersion === 9) {
    // IE9 的處理：動態載入 HTML5 Shiv 和專屬 CSS
    var script = document.createElement("script");
    script.src = "{{ url_for('static', filename='js/html5shiv.js') }}";
    document.head.appendChild(script);

    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.type = "text/css";
    link.media = "screen";
    link.href = "{{ url_for('static', filename='css/ie.css') }}";
    document.head.appendChild(link);
}
