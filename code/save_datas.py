import pymysql

class Database:
    def __init__(self, database_tag = 0):
        self.db = pymysql.connect(host = 'localhost', user = 'root', passwd = 'ptdb', db = 'MovieDatabase', charset = 'utf8')
        self.cur = self.db.cursor()
        #creat table
        self.table_name = 'movies_{0}'.format(database_tag)
        self.cur.execute(
            """create table if not exists %s (
                id int not null auto_increment,
                title varchar(255),
                original_title varchar(255),
                douban_id varchar(10),
                poster_url varchar(255),
                director varchar(100),
                writers varchar(150),
                actors text,
                type varchar(100),
                producer_area varchar(100),
                language varchar(50),
                release_data varchar(100),
                film_length varchar(100),
                other_title varchar(255),
                imdb_id varchar(20),
                douban_score varchar(10),
                plot text,
                primary key(id))charset=utf8""" % self.table_name
        )
        
    def insert(self, data):
        while True:
            pos = data['plot'].find('"')
            if pos == -1: break
            data['plot'] = data['plot'][:pos] + data['plot'][pos+1:]
        self.cur.execute(
            """insert into {0} (
                title, original_title, douban_id, poster_url, director, writers, actors, type, producer_area, 
                language, release_data, film_length, other_title, imdb_id, douban_score, plot)
                values(
                "%(title)s", "%(original_title)s", "%(douban_id)s", "%(poster_url)s", "%(director)s",
                "%(writers)s", "%(actors)s", "%(type)s", "%(producer_area)s", "%(language)s", "%(release_data)s",
                "%(film_length)s", "%(other_title)s", "%(imdb_id)s", "%(douban_score)s", "%(plot)s"
                )""".format(self.table_name) % data
        )
        self.db.commit()

    def close(self):
        self.db.close()
