from shakenfist_ci import base


class TestUpgrades(base.BaseTestCase):
    def test_upgraded_data_exists(self):
        # There is an upgraded namespace called 'upgrade'
        self.assertIn('upgrade', self.system_client.get_namespaces())

        # Collect networks and check
        networks_by_name = {}
        networks_by_uuid = {}
        for net in self.system_client.get_networks():
            networks_by_name['%s/%s' % (net['namespace'], net['name'])] = net
            networks_by_uuid[net['uuid']] = net

        self.assertIn('upgrade/upgrade-fe', networks_by_name)
        self.assertIn('upgrade/upgrade-be', networks_by_name)

        # Collect instances and check
        instances = {}
        for inst in self.system_client.get_instances():
            instances['%s/%s' % (inst['namespace'], inst['name'])] = inst

        # Determine interface information
        addresses = {}
        for name in ['upgrade/fe', 'upgrade/be-1', 'upgrade/be-2']:
            self.assertIn(name, instances)
            for iface in self.system_client.get_instance_interfaces(instances[name]['uuid']):
                net_name = networks_by_uuid.get(
                    iface['network_uuid'], {'name': 'unknown'})['name']
                addresses['%s/%s' % (name, net_name)] = iface['ipv4']

        print(addresses)

        # Ensure we can ping all instances
        self._test_ping(
            instances['upgrade/fe']['uuid'],
            networks_by_name['upgrade/upgrade-fe']['uuid'],
            addresses['upgrade/fe/upgrade-fe'],
            True, 10)
        self._test_ping(
            instances['upgrade/fe']['uuid'],
            networks_by_name['upgrade/upgrade-be']['uuid'],
            addresses['upgrade/fe/upgrade-be'],
            True, 10)

        self._test_ping(
            instances['upgrade/be-1']['uuid'],
            networks_by_name['upgrade/upgrade-be']['uuid'],
            addresses['upgrade/be-1/upgrade-be'],
            True, 10)
        self._test_ping(
            instances['upgrade/be-2']['uuid'],
            networks_by_name['upgrade/upgrade-be']['uuid'],
            addresses['upgrade/be-2/upgrade-be'],
            True, 10)
