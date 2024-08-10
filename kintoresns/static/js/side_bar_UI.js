(function (window, document) {

    var sidebar = document.getElementById('sidebar');
    var menuLink = document.getElementById('menuLink');

    function toggleSidebar(e) {
        e.preventDefault();
        sidebar.classList.toggle('active');
    }

    menuLink.addEventListener('click', toggleSidebar);

    // メインコンテンツや他の部分をクリックしたときにサイドバーを閉じる
    document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !menuLink.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });

}(this, this.document));
