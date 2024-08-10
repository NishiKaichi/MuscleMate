(function (window, document) {

    var allTrainee = document.getElementById('allTrainee');
    var allUsersPanel = document.getElementById('allUsersPanel');

    allTrainee.addEventListener('click', function() {
        if (allUsersPanel.classList.contains('active')) {
            allUsersPanel.classList.remove('active'); // パネルをスライドアウト
            setTimeout(function() {
                allUsersPanel.classList.add('hidden'); // スライドアウト後に非表示にする
            }, 300); // トランジションの時間に合わせて調整
        } else {
            allUsersPanel.classList.remove('hidden'); // パネルを表示
            setTimeout(function() {
                allUsersPanel.classList.add('active'); // パネルをスライドイン
            }, 10); // 微小な遅延をつけてスライドイン
        }
    });

    // クリック以外の部分をクリックするとパネルを閉じる
    document.addEventListener('click', function(e) {
        if (!allTrainee.contains(e.target) && !allUsersPanel.contains(e.target)) {
            if (allUsersPanel.classList.contains('active')) {
                allUsersPanel.classList.remove('active'); // パネルをスライドアウト
                setTimeout(function() {
                    allUsersPanel.classList.add('hidden'); // スライドアウト後に非表示にする
                }, 300); // トランジションの時間に合わせて調整
            }
        }
    });

}(this, this.document));
