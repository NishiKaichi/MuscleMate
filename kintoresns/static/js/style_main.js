function adjustMainPadding() {
    const header = document.querySelector('header');
    const main = document.getElementById('main');

    if (header && main) {
        // ヘッダーの下端の位置を計算
        const headerBottom = header.getBoundingClientRect().bottom;
        
        // #main の padding-top をヘッダーの下端に合わせる
        main.style.paddingTop = `${headerBottom}px`;        
    } 
}

window.addEventListener('resize', adjustMainPadding);
window.addEventListener('load', adjustMainPadding);
