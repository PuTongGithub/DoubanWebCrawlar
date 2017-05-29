import pymysql

class Database:
    def __init__(self, database_tag = 0):
        self.db = pymysql.connect(host = 'localhost', user = 'root', passwd = 'ptdb', db = 'MovieDatabase', charset = 'utf8mb4')
        self.cur = self.db.cursor()
        #creat table
        self.table_name = 'movies_{0}'.format(database_tag)
        self.cur.execute(
            """create table if not exists %s (
                id int not null auto_increment,
                title varchar(255),
                original_title varchar(255),
                douban_id varchar(20),
                poster_url varchar(255),
                director varchar(255),
                writers varchar(255),
                actors text,
                type varchar(255),
                producer_area varchar(255),
                language varchar(255),
                release_data varchar(255),
                film_length varchar(255),
                other_title varchar(255),
                imdb_id varchar(20),
                douban_score varchar(20),
                plot text,
                primary key(id))charset=utf8mb4""" % self.table_name
        )
        
    def insert(self, data):
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
