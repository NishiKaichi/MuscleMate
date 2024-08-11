function adjustLayout() {
    const header = document.querySelector('header');
    const main = document.getElementById('main');
    const postList = document.querySelector('.post-list');
    const footer = document.querySelector('footer');

    if (header && main && postList && footer) {
        // ヘッダーの高さを取得
        const headerHeight = header.offsetHeight;

        // ビューポートの高さからヘッダーとフッターの高さを引いて、mainの高さを計算
        const viewportHeight = window.innerHeight;
        const footerHeight = footer.offsetHeight;
        const mainHeight = viewportHeight - headerHeight - footerHeight;

        // main の高さを設定
        main.style.height = `${mainHeight}px`;

        // main のパディングを取得
        const mainPaddingTop = parseFloat(window.getComputedStyle(main).paddingTop);
        const mainPaddingBottom = parseFloat(window.getComputedStyle(main).paddingBottom);

        // パディングを考慮して post-list の max-height を設定
        const maxHeight = mainHeight - mainPaddingTop - mainPaddingBottom;
        postList.style.maxHeight = `${maxHeight}px`;

        console.log(`Header height: ${headerHeight}px, Footer height: ${footerHeight}px, Main height set to: ${main.style.height}, Post-list max-height set to: ${postList.style.maxHeight}`);
    } else {
        console.log('Header, main, post-list, or footer not found');
    }
}

window.addEventListener('resize', adjustLayout);
window.addEventListener('load', adjustLayout);

// スクロール位置を保存する
window.addEventListener("beforeunload", function () {
    localStorage.setItem("scrollPosition", window.scrollY);
  });

  // スクロール位置を復元する
  window.addEventListener("load", function () {
    const scrollPosition = localStorage.getItem("scrollPosition");
    if (scrollPosition) {
      window.scrollTo(0, parseInt(scrollPosition));
      localStorage.removeItem("scrollPosition"); // 一度復元したら削除
    }
  });