from src.config_loader import ConfigLoader
from src.utility import get_args
from src.wireguard_management import WireguardStats
from src.db import DB


def main(**kwargs):
	cfg = ConfigLoader(args.config)
	print(cfg.settings)
	print(cfg.vpns)
	wgconf = WireguardStats()
	db = DB()
	db.write_wireguard_stats(wgconf)


if __name__ == '__main__':
	args = get_args()
	wsgi = False
	main()
