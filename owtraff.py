from src.config_loader import OpenvpnConfigLoader
from src.utility import get_args
from src.wireguard_stats import WireguardStats
from src.openvpn_stats import OpenvpnStats
from src.db import DB


def main(**kwargs):
	ovpn_cfg = OpenvpnConfigLoader(args.config)
	wg_stats = WireguardStats()
	ovpn_stats = OpenvpnStats(ovpn_cfg)
	print(ovpn_stats.vpns)
	db = DB()
	db.write_wireguard_stats(wg_stats)


if __name__ == '__main__':
	args = get_args()
	wsgi = False
	main()
