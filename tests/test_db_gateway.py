import csv
from patsy.core.patsy_record import PatsyUtils
import unittest
from argparse import Namespace
from patsy.core.schema import Schema
from patsy.core.db_gateway import DbGateway
from patsy.core.load import Load
from typing import Dict


class TestDbGateway(unittest.TestCase):
    def setUp(self):
        test_db_files = [
            "tests/fixtures/db_gateway/colors_inventory.csv",
            "tests/fixtures/db_gateway/solar_system_inventory.csv"
        ]

        args = Namespace()
        args.database = ":memory:"
        self.gateway = DbGateway(args)
        schema = Schema(self.gateway)
        schema.create_schema()
        for file in test_db_files:
            load = Load(self.gateway)
            load.process_file(file)

    def test_get_all_batches(self):
        batches = self.gateway.get_all_batches()
        self.assertEqual(2, len(batches))
        batch_names = [batch.name for batch in batches]
        self.assertIn("TEST_COLORS", batch_names)
        self.assertIn("TEST_SOLAR_SYSTEM", batch_names)

    def test_get_batch_by_name__batch_does_not_exist(self):
        batch = self.gateway.get_batch_by_name("NON_EXISTENT_BATCH")
        self.assertIsNone(batch)

    def test_get_batch_by_name__batch_exists(self):
        batch = self.gateway.get_batch_by_name("TEST_COLORS")
        self.assertIsNotNone(batch)
        self.assertEqual("TEST_COLORS", batch.name)

    def test_get_batch_records__batch_does_not_exist(self):
        patsy_records = self.gateway.get_batch_records("NON_EXISTENT_BATCH")
        self.assertEqual(0, len(patsy_records))

    def test_get_batch_records__batch_exists(self):
        patsy_records = self.gateway.get_batch_records("TEST_COLORS")

        expected_patsy_records = []
        with open("tests/fixtures/db_gateway/colors_inventory.csv") as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                expected_patsy_records.append(PatsyUtils.from_inventory_csv(row))

        self.assertGreater(len(expected_patsy_records), 0)
        self.assertEqual(len(expected_patsy_records), len(patsy_records))

        for p in patsy_records:
            self.assertIn(p, expected_patsy_records)
