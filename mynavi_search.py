import os
from numpy import true_divide
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd
from bs4 import BeautifulSoup
import datetime as dt
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
import eel

pd.set_option('display.unicode.east_asian_width', True)

# Chromeを起動する関数
def set_driver(driver_path, headless_flg):

    if "chrome" in driver_path:
        options = ChromeOptions()
    else:
        options = Options()

    # ヘッドレスモード（画面非表示モード）の設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)


# ♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪
# ページ内のデータ取得用関数
# DataFrameと、次ページへのリンクのタグ返す
# ♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪

def page_process(page_html):
    # htmlをparse
    parse_html = BeautifulSoup(page_html, 'html.parser')

    ### 会社名を取得　→　co_name-list
    #　h3 クラス名が「cassetteRecruit」で始まる　をリストに
    h3_lists = parse_html.find_all('h3', class_=re.compile('^cassetteRecruit'))
    #　h3 テキストをリストに
    h3_text_lists=[ list.string for list in h3_lists ]  
    #　テキストから会社名だけ抜いて　リストに
    co_name_list = [list.split(' |')[0] for list in h3_text_lists]
    print(str(len(co_name_list)))

    ### 情報更新日を取得　→　update_list
    #　情報更新日の<p>を取得　クラス名が「updateDate」で終わる
    update_p_lists = parse_html.find_all('p', class_=re.compile('updateDate$'))
    #　<p>の中の<span>の文字列を抜き出す
    update_list=[list.select('span')[0].string for list in update_p_lists]
    print(str(len(update_list)))

    #　給与の情報を取得　→　salary_list
    #　tableタグを取得
    # DataFrameに。１列目をindexに指定
    tables = parse_html.find_all('table', class_='tableCondition')
    df = pd.read_html(str(tables), header=None, index_col=0)
    #　indexが給与の値を取得
    salary_list = [ table.loc["給与",1] for table in df ]
    print(str(len(salary_list)))
    ###listからDataFrameへ
    df2 = pd.DataFrame({'会社名':co_name_list, '給与':salary_list, '情報更新日':update_list})

    is_next = parse_html.select_one('.pager__next > .iconFont--arrowLeft')
    
    return df2, is_next


# 現在時刻を取得して成形
def time_form():
    now_time = dt.datetime.now()
    formated_time = f"{now_time:%Y/%m/%d-%H:%M:%S}"
    return formated_time


# スクレイピング処理
def do_scraping(search_keyword):
    now = time_form()
    eel.write_logs(f"{now}：処理を開始しました。")

    url = "https://tenshoku.mynavi.jp/"
    
    #ログファイル用の準備
    i =  0  #ページ数カウンター

    # driverを起動
    if os.name == 'nt': #Windows
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)

    # Webサイトを開く
    driver.set_window_size(700,800)
    driver.get(f"{url}/list/kw{search_keyword}/?jobsearchType=14&searchType=18")
    time.sleep(5)

    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)

    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(3)

    #空のDataFrame準備
    df_list = pd.DataFrame()

    # 現在のページのhtml取得
    page_html = driver.page_source


    try:
        #################################
        # ページ終了まで繰り返し取得
        while True:
            page_data = page_process(page_html)
            # print(is_next)
            df_list=pd.concat([df_list,page_data[0]])  #データフレームを結合
            #ページカウンターセット
            i += 1
            #jsを呼び出してテキストエリアに作業進捗を追記
            now = time_form()
            eel.write_logs(f"{now}：{i:02}ページ目完了")

            if page_data[1] == None:
                break
            else:
                next_url = url + page_data[1].get('href')
                driver.get(next_url)
                time.sleep(5)
                page_html = driver.page_source

        ###### end while ################

        df_list= df_list.reset_index(drop = True)
        df_list.index = df_list.index + 1
        data_count = str(len(df_list))

        now = time_form()
        eel.write_logs(f"{now}：{data_count}件　情報取得完了")

        df_list.to_csv(f'mynavi_{search_keyword}.csv', encoding='utf-8_sig') #utf-8-sig
        now = time_form()
        eel.write_logs(f"{now}：csvファイル出力完了")

        # スクレイピング実行ウィンドウを閉じる
        driver.close()
        

    except Exception as e:
        now = time_form()
        eel.write_logs(f"{now}：エラー発生\n\n※※エラー内容：{e} ")
        print("エラーが発生しました。処理を終了します。")
        print("エラー内容：" , e)

    # ♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪
    # ♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪