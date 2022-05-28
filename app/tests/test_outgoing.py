import unittest
from fastapi.testclient import TestClient

from app.codes.p2p.outgoing import get_excluded_node_list, get_excluded_peers_to_broadcast

from ..main import app

client = TestClient(app)


class OutgoingTest(unittest.TestCase):
    peers = [
        {'id': '11.12.13.14', 'address': '11.12.13.14'},
        {'id': '11.12.13.15', 'address': '11.12.13.15'},
        {'id': '11.12.13.16', 'address': '11.12.13.16'},
        {'id': '11.12.13.17', 'address': '11.12.13.17'},
        {'id': '11.12.13.18', 'address': '11.12.13.18'},
    ]

    def test_get_excluded_peers_to_broadcast(self):
        exclude_nodes = ['11.12.13.16', '11.12.13.17']
        
        peers = get_excluded_peers_to_broadcast(self.peers, exclude_nodes)

        expected_peers = [
            {'id': '11.12.13.14', 'address': '11.12.13.14'},
            {'id': '11.12.13.15', 'address': '11.12.13.15'},
            {'id': '11.12.13.18', 'address': '11.12.13.18'},
        ]
        self.assertListEqual(peers, expected_peers)
    
    def test_get_excluded_node_list(self):
        already_broadcasted_nodes = ['11.12.13.11', '11.12.13.19']
        peer_addresses = list(map(lambda p: p['address'], self.peers))
        combined_exclusion_list = get_excluded_node_list(self.peers, already_broadcasted_nodes)
        expected_combined_exclusion_list = peer_addresses + already_broadcasted_nodes
        self.assertEqual(len(combined_exclusion_list), len(expected_combined_exclusion_list))
        self.assertSetEqual(set(combined_exclusion_list), set(expected_combined_exclusion_list))
