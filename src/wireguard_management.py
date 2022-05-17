import subprocess
from collections import deque


class WireguardStats(object):

	def __init__(self):
		self.pconf = {}
		dump_data = self.get_dump_data()
		self.pconf = self.parse_wg_dump(dump_data)
		print(self.pconf)

	@staticmethod
	def get_dump_data() -> list[str]:
		command = ['wg', 'show', 'wg0', 'dump']
		out_str = subprocess.run(command, stdout=subprocess.PIPE, text=True)
		return out_str.stdout.splitlines()

	@staticmethod
	def parse_wg_dump(dump_data: list[str]) -> dict[str, any]:
		all_users_stat: dict[str, any] = {}
		user_section = False

		print(dump_data)

		for line in dump_data:
			user_stat: dict[str, any] = {}
			already_connected = True
			if not user_section:  # pass first string
				user_section = True
				continue

			list_words = deque(line.split('\t'))
			user_stat['peer_name'] = list_words.popleft()
			list_words.popleft()  # pass private key
			endpoint_ip = list_words.popleft()
			if endpoint_ip.startswith('none'):  # never connecting
				already_connected = False

			if already_connected:
				user_stat['endpoint_ip'] = endpoint_ip.split(':')[0]
			int_ips = list_words.popleft().split(',')
			user_stat['allowed_ip4'] = int_ips[0].split('/')[0]
			user_stat['allowed_ip6'] = int_ips[1].split('/')[0]

			if not already_connected:
				user_stat['endpoint_ip'] = None
				user_stat['latest_handshake'] = None
				user_stat['data_recv'] = 0
				user_stat['data_sent'] = 0
				continue

			user_stat['latest_handshake'] = int(list_words.popleft())
			user_stat['data_recv'] = int(list_words.popleft())
			user_stat['data_sent'] = int(list_words.popleft())

			all_users_stat[user_stat['peer_name']] = user_stat

		return all_users_stat
