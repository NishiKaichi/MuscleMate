(function (window, document) {

    var favTrainee = document.getElementById('favTrainee');
    var favUsersPanel = document.getElementById('favUsersPanel');

    favTrainee.addEventListener('click', function() {
        if (favUsersPanel.classList.contains('active')) {
            favUsersPanel.classList.remove('active'); // パネルをスライドアウト
            setTimeout(function() {
                favUsersPanel.classList.add('hidden'); // スライドアウト後に非表示にする
            }, 0); // トランジションの時間に合わせて調整
        } else {
            favUsersPanel.classList.remove('hidden'); // パネルを表示
            setTimeout(function() {
                favUsersPanel.classList.add('active'); // パネルをスライドイン
            }, 0); // 微小な遅延をつけてスライドイン
        }
    });

    // クリック以外の部分をクリックするとパネルを閉じる
    document.addEventListener('click', function(e) {
        if (!favTrainee.contains(e.target) && !favUsersPanel.contains(e.target)) {
            if (favUsersPanel.classList.contains('active')) {
                favUsersPanel.classList.remove('active'); // パネルをスライドアウト
                setTimeout(function() {
                    favUsersPanel.classList.add('hidden'); // スライドアウト後に非表示にする
                }, 0); // トランジションの時間に合わせて調整
            }
        }
    });

}(this, this.document));
