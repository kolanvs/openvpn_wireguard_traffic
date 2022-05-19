import sqlite3
import sys
import time
from itertools import chain
from src.wireguard_management import WireguardStats
from src.utility import flatten


class DB(object):
    def __init__(self):
        print("Here1")
        self.dbname = "sqlite3.db"
        try:
            conn = sqlite3.connect(self.dbname)
        except sqlite3.Error:
            sys.exit(1)

        print("Here2")

        self.curs = conn.cursor()
        self.conn = conn

        if self.check_need_bootstrap():
            print("Need bootstrap!")
            self.bootstrap_db()

    def bootstrap_db(self):
        create_peers_table = """
							create table peers
							(
								id		integer primary key,
								name	text not null
							)
							"""

        create_stats_table = """
								create table stats
								(
								id				integer primary key,
								peer_id			integer,
								timestamp		integer,
								data_recv		integer,
								data_sent		integer
								)
								"""

        print("Bootstrapping!")

        self.curs.execute(create_peers_table)
        self.curs.execute(create_stats_table)

    def check_need_bootstrap(self):
        check_peers = """
						select * from sqlite_master
						where tbl_name = 'peers'
						"""

        check_stats = """
						select * from sqlite_master
						where tbl_name = 'stats'
						"""

        print("Check bootstrap")
        return (len(self.curs.execute(check_peers).fetchall()) == 0) or (
            len(self.curs.execute(check_stats).fetchall()) == 0
        )

    def write_wireguard_stats(self, wg_stats: WireguardStats):
        peer_names_conf = wg_stats.pconf.keys()
        print(peer_names_conf)
        peer_names_db = list(
            chain(*self.curs.execute("select name from peers").fetchall())
        )
        print(peer_names_db)
        for peer_name in peer_names_conf:
            print(peer_name)
            if peer_name not in peer_names_db:
                self.curs.execute(
                    "insert into peers (name) values ('{0}')".format(peer_name)
                )
                self.conn.commit()
        peers = {
            k[1]: k[0]
            for k in self.curs.execute("select id, name from peers").fetchall()
        }

        for peer_name in peer_names_conf:
            peer_stat = wg_stats.pconf[peer_name]
            print(peer_stat)
            print(
                "insert into stats (peer_id, timestamp, data_recv, data_sent)"
                "values ('{0}, {1}, {2}, {3}')".format(
                    peers[peer_name],
                    int(time.time()),
                    peer_stat["data_recv"],
                    peer_stat["data_sent"],
                )
            )
            self.curs.execute(
                "insert into stats (peer_id, timestamp, data_recv, data_sent)"
                "values ({0}, {1}, {2}, {3})".format(
                    peers[peer_name],
                    int(time.time()),
                    peer_stat["data_recv"],
                    peer_stat["data_sent"],
                )
            )

        self.conn.commit()
