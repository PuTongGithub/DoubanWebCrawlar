from get_douban_datas import Douban
from save_datas import Database
douban = Douban()
db = Database(1)
for data in douban.get_all_datas():
    db.insert(data)
    print(data['douban_id'], data['title'])
db.close()