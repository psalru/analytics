import unittest
from functions import *


class TestingFunctions(unittest.TestCase):
    affiliation_string_variants = [
        '[p_1; p_2; p_3] u_one, address_u_one, country_1; ' +
        '[p_2] u_two, address_u_two, country_1; ' +
        '[p_3] u_three, address_u_three, country_2',

        '[p_1; p_2; p_3] u_one, address_u_one, country_1; ' +
        '[p_1] u_one, depth_1_u_one, address_u_one, country_1; ' +
        '[p_2] u_one, depth_2_u_two, address_u_two, country_1; ' +
        '[p_3] u_two, address_u_two, country_2; ' +
        '[p_1; p_4] u_three, address_u_three, country_2',

        '[p_1; p_2; p_3; p_4] u_one, depth_1_u_one, address_u_one, country_1; ' +
        '[p_3] u_one, depth_2_u_one, address_u_two, country_1; ' +
        '[p_4] u_two, depth_1_u_two, address_u_two, country_2',
    ]

    affiliation_list = ['u_one', 'u_two']

    def test_get_magic_string(self):
        self.assertEqual(get_magic_string('ITMO UNIVERSITY'), 'itmouniversity')
        self.assertEqual(get_magic_string('a;P_9df*q23U&%4fns8#fHa'), 'apdfqufnsfha')

    def test_get_affiliation_count(self):
        self.assertEqual(get_affiliation_count(self.affiliation_string_variants[0]), 3)
        self.assertEqual(get_affiliation_count(self.affiliation_string_variants[1]), 3)
        self.assertEqual(get_affiliation_count(self.affiliation_string_variants[2]), 2)
        self.assertEqual(get_affiliation_count(self.affiliation_string_variants[0], self.affiliation_list), 2)
        self.assertEqual(get_affiliation_count(self.affiliation_string_variants[1], self.affiliation_list), 2)
        self.assertEqual(get_affiliation_count(self.affiliation_string_variants[2], self.affiliation_list), 1)

    def test_get_affiliation_data(self):
        self.assertDictEqual(get_my_affiliation_data(self.affiliation_string_variants[0], self.affiliation_list), {
            'packages': [
                {
                    'name': 'u_one',
                    'authors': ['p_1', 'p_2', 'p_3']
                },
                {
                    'name': 'u_two',
                    'authors': ['p_2']
                }
            ],
            'count_affiliations_by_author': {
                'p_1': 1,
                'p_2': 1,
                'p_3': 2,
            },
        })
        self.assertDictEqual(get_my_affiliation_data(self.affiliation_string_variants[1], self.affiliation_list), {
            'packages': [
                {
                    'name': 'u_one',
                    'authors': ['p_1', 'p_2', 'p_3']
                },
                {
                    'name': 'u_one',
                    'authors': ['p_1']
                },
                {
                    'name': 'u_one',
                    'authors': ['p_2']
                },
                {
                    'name': 'u_two',
                    'authors': ['p_3']
                }
            ],
            'count_affiliations_by_author': {
                'p_1': 2,
                'p_2': 1,
                'p_3': 1
            },
        })
        self.assertDictEqual(get_my_affiliation_data(self.affiliation_string_variants[2], self.affiliation_list), {
            'packages': [
                {
                    'name': 'u_one',
                    'authors': ['p_1', 'p_2', 'p_3', 'p_4']
                },
                {
                    'name': 'u_one',
                    'authors': ['p_3']
                },
                {
                    'name': 'u_two',
                    'authors': ['p_4']
                }
            ],
            'count_affiliations_by_author': {
                'p_1': 1,
                'p_2': 1,
                'p_3': 1,
                'p_4': 1
            },
        })

    def test_get_faction(self):
        self.assertEqual(get_faction({
            'authors_count': 3,
            'my_affiliation': get_my_affiliation_data(self.affiliation_string_variants[0], self.affiliation_list)
        }), 0.8333333333333333)
        self.assertEqual(get_faction({
            'authors_count': 4,
            'my_affiliation': get_my_affiliation_data(self.affiliation_string_variants[1], self.affiliation_list)
        }), 0.625)
        self.assertEqual(get_faction({
            'authors_count': 4,
            'my_affiliation': get_my_affiliation_data(self.affiliation_string_variants[2], self.affiliation_list)
        }), 1)


if __name__ == '__main__':
    unittest.main()
