"""Contrato local de extension0203; ninguna prueba llama proveedores."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import extension0203 as e


class Extension0203Tests(unittest.TestCase):
    def test_schedule_contains_exact_93_remaining_in_original_order(self):
        with patch.object(e, 'state', return_value={'niveles': list(e.e02.LEVELS)}):
            rows = e.schedule('principal')
        self.assertEqual(len(rows), 93)
        self.assertEqual(rows[0]['id'], 'principal-07-planificador-xhigh-2')
        self.assertEqual(rows[0]['orden'], 28)
        self.assertEqual([r['orden'] for r in rows], list(range(28, 121)))

    def test_api_command_has_no_credentials_file_and_no_clearenv_or_secret_in_argv(self):
        args = e.claude_api_command(Path('/work'), 'high')
        joined = ' '.join(args)
        self.assertNotIn('.credentials.json', joined)
        self.assertNotIn('--clearenv', args)
        self.assertNotIn('ANTHROPIC_API_KEY', joined)
        self.assertIn('claude-fable-5-2', args)
        public = e.e02.public_command(args)
        for flag in ('--restricted', '--strict-mcp-config', '--disable-slash-commands', '--no-session-persistence', '--no-chrome'):
            self.assertIn(flag, public)

    def test_api_env_uses_only_six_minimal_vars(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'sk-ant-test-dummy', 'EXTRA_LEAK': 'nope'}, clear=True):
            env = e.claude_api_env()
        self.assertEqual(set(env.keys()), {'PATH', 'LANG', 'HOME', 'PYTHONDONTWRITEBYTECODE', 'PYTHONHASHSEED', 'ANTHROPIC_API_KEY'})
        self.assertEqual(env['ANTHROPIC_API_KEY'], 'sk-ant-test-dummy')

    def test_api_billing_and_key_errors_categorized(self):
        self.assertEqual(e.category('Your credit balance is too low to access the Anthropic API'), 'cuota')
        self.assertEqual(e.category('invalid x-api-key'), 'autenticacion')

    def test_interrupted_run_is_not_retried(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(e, 'ART03', Path(temp)), patch.object(e, 'state', return_value={'estado': 'sondeado', 'niveles': ['low']}), patch.object(e, 'run_one') as call:
            item = e.schedule('piloto')[0]
            e.e02.write(Path(temp) / 'fable' / 'iniciadas' / (item['id'] + '.json'), item)
            with self.assertRaisesRegex(RuntimeError, 'sin cierre'):
                e.run_matrix('piloto')
            call.assert_not_called()


if __name__ == '__main__':
    unittest.main()
