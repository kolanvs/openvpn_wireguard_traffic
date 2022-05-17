import sqlite3
import sys

create_peers_table = '''
                    create table peers
                    (
                        id               integer primary key,
                        name             text not null
                    )
                    '''

check_bootstrap = '''
                    select * from sqlite_master
                    where tbl_name = 'peers'
                  '''


class OpenvpnMgmtInterface(object):

    def __init__(self):

        create_peers_table = '''
                                create table peers
                                (
                                    id               integer primary key,
                                    name             text not null
                                )
                                '''

        self.dbname = 'sqlite3.db'
        try:
            conn = sqlite3.connect(self.dbname)
        except sqlite3.Error:
            sys.exit(1)

        curs = conn.cursor()

        check_peers = '''
                        select * from sqlite_master
                        where tbl_name = 'peers'
                      '''

        check_stats = '''
                        select * from sqlite_master
                        where tbl_name = 'stats'
                      '''

        need_bootstrap = (len(curs.execute(check_peers).fetchall()) > 0) and \
                         (len(curs.execute(check_stats).fetchall()) > 0)





