import sqlite3
import sys
import time
from itertools import chain
from src.wireguard_stats import WireguardStats
from src.utility import flatten


class DB(object):
	def __init__(self):
		self.dbname = "sqlite3.db"
		try:
			conn = sqlite3.connect(self.dbname)
		except sqlite3.Error:
			sys.exit(1)

		self.curs = conn.cursor()
		self.conn = conn

		if self.check_need_bootstrap_wireguard():
			self.bootstrap_db_wireguard()

		if self.check_need_bootstrap_openvpn():
			self.bootstrap_db_openvpn()

	def bootstrap_db_wireguard(self):
		create_wg_peers_table = """
							create table wg_peers
							(
								id		integer primary key,
								name	text not null
							)
							"""
		create_wg_stats_table = """
								create table wg_stats
								(
								id				integer primary key,
								peer_id			integer,
								timestamp		integer,
								data_recv		integer,
								data_sent		integer
								)
								"""
		self.curs.execute(create_wg_peers_table)
		self.curs.execute(create_wg_stats_table)

	def bootstrap_db_openvpn(self):
		create_ovpn_clients_table = """
							create table ovpn_clients
							(
								id		integer primary key,
								name	text not null
							)
							"""
		create_ovpn_stats_table = """
								create table ovpn_stats
								(
								id				integer primary key,
								peer_id			integer,
								timestamp		integer,
								data_recv		integer,
								data_sent		integer
								)
								"""
		self.curs.execute(create_ovpn_clients_table)
		self.curs.execute(create_ovpn_stats_table)

	def check_need_bootstrap_wireguard(self):
		check_wg_peers = """
						select * from sqlite_master
						where tbl_name = 'wg_peers'
						"""
		check_wg_stats = """
						select * from sqlite_master
						where tbl_name = 'wg_stats'
						"""
		return (len(self.curs.execute(check_wg_peers).fetchall()) == 0) or (
				len(self.curs.execute(check_wg_stats).fetchall()) == 0
		)

	def check_need_bootstrap_openvpn(self):
		check_ovpn_clients = """
						select * from sqlite_master
						where tbl_name = 'ovpn_clients'
						"""

		check_ovpn_stats = """
                        select * from sqlite_master
                        where tbl_name = 'ovpn_stats'
                        """

		return (len(self.curs.execute(check_ovpn_clients).fetchall()) == 0) or (
				len(self.curs.execute(check_ovpn_stats).fetchall()) == 0
		)

	def write_wireguard_wg_stats(self, wg_stats: WireguardStats):
		wg_peer_names_conf = wg_stats.pconf.keys()
		wg_peer_names_db = list(
			chain(*self.curs.execute("select name from wg_peers").fetchall())
		)
		for wg_peer_name in wg_peer_names_conf:
			if wg_peer_name not in wg_peer_names_db:
				self.curs.execute(
					"insert into wg_peers (name) values ('{0}')".format(wg_peer_name)
				)
				self.conn.commit()
		wg_peers = {
			k[1]: k[0]
			for k in self.curs.execute("select id, name from wg_peers").fetchall()
		}

		for wg_peer_name in wg_peer_names_conf:
			wg_peer_stat = wg_stats.pconf[wg_peer_name]
			self.curs.execute(
				"insert into wg_stats (peer_id, timestamp, data_recv, data_sent)"
				"values ({0}, {1}, {2}, {3})".format(
					wg_peers[wg_peer_name],
					int(time.time()),
					wg_peer_stat["data_recv"],
					wg_peer_stat["data_sent"],
				)
			)

		self.conn.commit()
