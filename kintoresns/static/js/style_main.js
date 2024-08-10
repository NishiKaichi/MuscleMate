function adjustLayout() {
    const header = document.querySelector('header');
    const main = document.getElementById('main');
    const postList = document.querySelector('.post-list');

    if (header && main && postList) {
        // ヘッダーの高さを取得
        const headerHeight = header.offsetHeight;

        // ビューポートの高さからヘッダーの高さを引いて、mainの高さを計算
        const viewportHeight = window.innerHeight;
        const mainHeight = viewportHeight - headerHeight;

        // パディングを考慮して main の高さを設定
        main.style.height = `${mainHeight}px`;

        // main のパディングを取得
        const mainPaddingTop = parseFloat(window.getComputedStyle(main).paddingTop);
        const mainPaddingBottom = parseFloat(window.getComputedStyle(main).paddingBottom);

        // パディングを考慮して post-list の max-height を設定
        const maxHeight = mainHeight - mainPaddingTop - mainPaddingBottom;
        postList.style.maxHeight = `${maxHeight}px`;

        /*console.log(`Header height: ${headerHeight}px, Main height set to: ${main.style.height}, Post-list max-height set to: ${postList.style.maxHeight}`);
    } else {
        console.log('Header, main, or post-list not found');*/
    }
}

window.addEventListener('resize', adjustLayout);
window.addEventListener('load', adjustLayout);
