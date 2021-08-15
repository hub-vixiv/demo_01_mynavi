// ウィンドウ表示時に
// キーワードのテキストボックスに
// フォーカス
text_keyword.focus();

// 検索ボタンを押したら
// テキストエリアクリア
// 検索キーワードをテキストエリアへ書き込む
// pyへキーワードを渡す
function btn_search_click(){
    keyword = text_keyword.value;
    area_logs.value = "";
    // スクレイピングするpy呼び出す
    eel.do_scraping(keyword)();
}


// ログをテキストエリアへ書き込む
// pyから呼び出す
eel.expose(write_logs)
function write_logs(logs){
    area_logs.value += logs + "\n" ;
}