import eel
import desktop
import mynavi_search

app_name="html"
end_point="index.html"
size=(450,550)

# スクレイピング実行
@eel.expose
def do_scraping(search_keyword):
    mynavi_search.do_scraping(search_keyword)


desktop.start(app_name,end_point,size)