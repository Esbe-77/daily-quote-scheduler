import ast
import json
import os
from pathlib import Path
import random
import runpy
import smtplib
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from rotation import Rotation, content_id


ROOT = Path(__file__).resolve().parents[1]


def content_pools():
    tree = ast.parse((ROOT / 'Quotes.py').read_text(encoding='utf-8'))
    constants = {node.targets[0].id: ast.literal_eval(node.value)
                 for node in tree.body if isinstance(node, ast.Assign)
                 and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id in ('PASSAGES', 'CHESS_LESSONS')}
    return {
        'quotes': [q['quote'] for q in json.loads((ROOT / 'stoic_quotes.json').read_text(encoding='utf-8'))],
        'readings': [p[2] for p in constants['PASSAGES']],
        'chess': [p[1] for p in constants['CHESS_LESSONS']],
    }


class RotationTests(unittest.TestCase):
    def test_every_actual_item_gets_a_turn_before_repeats_across_restarts(self):
        pools = content_pools()
        sizes = {group: len({content_id(text) for text in texts}) for group, texts in pools.items()}
        deliveries = {group: [] for group in pools}
        with tempfile.TemporaryDirectory() as directory, patch('rotation.random.choice', side_effect=random.Random(42).choice):
            path = Path(directory) / 'history.json'
            for _ in range(max(sizes.values()) * 3):
                rotation = Rotation(path)
                for group, texts in pools.items():
                    selected = rotation.choose(group, texts)[0]
                    deliveries[group].append(content_id(texts[selected]))
                rotation.save()
            for group, size in sizes.items():
                for start in range(0, len(deliveries[group]) - size + 1, size):
                    self.assertEqual(len(set(deliveries[group][start:start + size])), size, group)
                self.assertTrue(all(a != b for a, b in zip(deliveries[group], deliveries[group][1:])))

    def test_duplicate_text_is_only_one_slot(self):
        self.assertEqual(content_id('Be kind — always.'), content_id('BE KIND - always!'))
        with tempfile.TemporaryDirectory() as directory:
            rotation = Rotation(Path(directory) / 'history.json')
            texts = ['Be kind — always.', 'BE KIND - always!', 'Be patient.']
            selected = rotation.choose('quotes', texts, 2)
            self.assertEqual(len({content_id(texts[i]) for i in selected}), 2)
            with self.assertRaises(ValueError):
                rotation.choose('quotes', texts, 3)

    def test_reordering_addition_and_removal_preserve_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'history.json'
            rotation = Rotation(path)
            selected = rotation.choose('quotes', ['alpha', 'beta'])[0]
            rotation.save()
            rotation = Rotation(path)
            reversed_texts = ['beta', 'alpha']
            next_index = rotation.choose('quotes', reversed_texts)[0]
            self.assertNotEqual(reversed_texts[next_index], ['alpha', 'beta'][selected])
            rotation.save()
            rotation = Rotation(path)
            self.assertEqual(rotation.choose('quotes', ['beta', 'new', 'alpha']), [1])
            rotation.save()
            rotation = Rotation(path)
            self.assertEqual(rotation.choose('quotes', ['new']), [0])

    def test_unsaved_selection_does_not_advance_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'history.json'
            rotation = Rotation(path)
            rotation.choose('quotes', ['alpha'])
            self.assertFalse(path.exists())
            self.assertEqual(Rotation(path).state['sequence'], 0)

    def test_corrupt_history_fails_instead_of_resetting(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'history.json'
            for data in ('broken', '{}', '{"version":1,"sequence":1,"groups":{"quotes":{"x":2}}}'):
                path.write_text(data, encoding='utf-8')
                with self.assertRaises(ValueError):
                    Rotation(path)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.previous = Path.cwd()
        os.chdir(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.addCleanup(os.chdir, self.previous)
        Path('stoic_quotes.json').write_bytes((ROOT / 'stoic_quotes.json').read_bytes())
        self.server = MagicMock()
        self.server.__enter__.return_value = self.server
        self.server.sendmail.return_value = {}
        self.credentials = {'EMAIL_SENDER': 'sender@example.invalid', 'EMAIL_PASSWORD': 'dummy', 'EMAIL_RECEIVER': 'receiver@example.invalid'}

    def run_delivery(self):
        with patch.dict(os.environ, self.credentials), patch('smtplib.SMTP', return_value=self.server), patch('socket.socket', side_effect=AssertionError('Real network access forbidden')):
            return runpy.run_path(str(ROOT / 'Quotes.py'), run_name='__main__')

    def test_success_saves_all_three_selections_only_after_send(self):
        def accepted(*args):
            self.assertFalse(Path('rotation_state.json').exists())
            return {}
        self.server.sendmail.side_effect = accepted
        state = self.run_delivery()
        saved = Rotation().state
        self.assertEqual(set(saved['groups']), {'quotes', 'readings', 'chess'})
        self.assertEqual(saved['sequence'], 3)
        self.assertIn("Today's thought, chess, and reading", self.server.sendmail.call_args.args[2])
        self.assertIn(state['passage_title'], state['html_body'])
        self.assertEqual(Path('stoic_quotes.json').read_bytes(), (ROOT / 'stoic_quotes.json').read_bytes())

    def test_failed_email_leaves_existing_history_unchanged(self):
        Rotation().save()
        original = Path('rotation_state.json').read_bytes()
        self.server.sendmail.side_effect = smtplib.SMTPException('Simulated failure')
        with self.assertRaises(smtplib.SMTPException):
            self.run_delivery()
        self.assertEqual(Path('rotation_state.json').read_bytes(), original)

    def test_refused_recipient_does_not_save_history(self):
        self.server.sendmail.return_value = {'receiver@example.invalid': (550, b'Rejected')}
        with self.assertRaises(smtplib.SMTPRecipientsRefused):
            self.run_delivery()
        self.assertFalse(Path('rotation_state.json').exists())

    def test_missing_credentials_does_not_save_history(self):
        self.credentials['EMAIL_PASSWORD'] = ''
        with self.assertRaises(SystemExit):
            self.run_delivery()
        self.server.sendmail.assert_not_called()
        self.assertFalse(Path('rotation_state.json').exists())

    def test_source_links_and_legacy_quotes_render_safely(self):
        state = self.run_delivery()
        render = state['quote_html']
        rendered = render({'quote': 'A < B & C', 'source': {'work': 'A & B', 'url': 'https://example.invalid/?a=1&b=2', 'translator': 'Translator'}})
        self.assertIn('A &lt; B &amp; C', rendered)
        self.assertIn('https://example.invalid/?a=1&amp;b=2', rendered)
        self.assertIn('translated by Translator', rendered)
        self.assertNotIn('<a ', render({'quote': 'A legacy quotation'}))


if __name__ == '__main__':
    unittest.main()
