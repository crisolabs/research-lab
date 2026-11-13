"""Contrato local del suplemento; ninguna prueba llama proveedores."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import extension02 as e


class UsageTests(unittest.TestCase):
    def test_codex_cached_and_reasoning_not_double_counted(self):
        obj = {'type': 'turn.completed', 'usage': {'input_tokens': 100, 'cached_input_tokens': 80, 'output_tokens': 20, 'reasoning_output_tokens': 7}}
        fields, receipt, _, _ = e.parse('codex', json.dumps(obj).encode())
        self.assertEqual(fields['tokens_totales'], 120)
        self.assertEqual(receipt['uso'], obj['usage'])

    def test_claude_disjoint_cache_categories_and_raw_model_usage(self):
        obj = {'type': 'result', 'usage': {'input_tokens': 10, 'output_tokens': 4, 'cache_creation_input_tokens': 30, 'cache_read_input_tokens': 40, 'thinking_tokens': 2, 'cache_creation': {'ephemeral_5m_input_tokens': 30}}, 'modelUsage': {'claude-fable-5-2': {'inputTokens': 10, 'outputTokens': 4}}, 'duration_ms': 123, 'duration_api_ms': 100, 'num_turns': 2, 'result': 'PRIVATE TEXT MUST NOT PERSIST'}
        fields, receipt, effective, error = e.parse('claude', json.dumps(obj).encode())
        self.assertEqual(fields['tokens_totales'], 84)
        self.assertEqual(receipt['uso'], obj['usage'])
        self.assertEqual(receipt['uso_por_modelo'], obj['modelUsage'])
        self.assertEqual(effective, 'claude-fable-5-2')
        self.assertEqual(receipt['num_turns'], 2)
        self.assertNotIn('PRIVATE', json.dumps(receipt))
        self.assertEqual(error, '')

    def test_missing_usage_is_not_zero(self):
        for cli in ('codex', 'claude'):
            fields, _, _, _ = e.parse(cli, b'{"type":"result","usage":{"input_tokens":2}}')
            self.assertEqual(fields['tokens_totales'], '')
        fields, _, _, _ = e.parse('claude', b'{"type":"result","usage":{"input_tokens":0,"output_tokens":0}}')
        self.assertEqual(fields['tokens_totales'], 0)

    def test_errors_not_confused_with_effort_or_model(self):
        self.assertEqual(e.category('Rate limit reached: model effort max'), 'cuota')
        self.assertEqual(e.category('Model not found'), 'modelo_no_disponible')
        self.assertEqual(e.category('Model does not support effort max'), 'nivel_no_admitido')
        self.assertEqual(e.category('Invalid OAuth token'), 'autenticacion')
        self.assertEqual(e.category('Connection refused'), 'infraestructura')

    def test_error_sanitization(self):
        email = '@'.join(('person', '.'.join(('example', 'org'))))
        personal_root = '/'.join(('', 'home', ''))
        synthetic_path = personal_root + '/'.join(('person', 'private'))
        message = f'Contact {email} at {synthetic_path} with Bearer some-secret-value and https://example.org/?token=abc'
        cleaned = e.clean(message)
        for private in (email, personal_root, 'some-secret-value', 'token=abc'):
            self.assertNotIn(private, cleaned)


class WorkflowTests(unittest.TestCase):
    def test_frozen_bank_unchanged(self):
        e.medir.check_frozen()
        self.assertEqual(len(e.medir.bank_hashes()), 34)

    def test_schedule_is_balanced_deterministic_and_pilot_excluded(self):
        with patch.object(e, 'state', return_value={'niveles': ['low', 'high']}):
            one = e.schedule('fable', 'principal')
            self.assertEqual(one, e.schedule('fable', 'principal'))
            self.assertEqual(len(one), 48)
            self.assertEqual(len({r['id'] for r in one}), 48)
            for task in e.medir.tasks():
                for level in ('low', 'high'):
                    self.assertEqual(sum(r['tarea'] == task['id'] and r['nivel'] == level for r in one), 3)
            pilot = e.schedule('fable', 'piloto')
            self.assertEqual(len(pilot), 1)
            self.assertEqual(pilot[0]['nivel'], 'low')
            self.assertFalse({r['id'] for r in one} & {r['id'] for r in pilot})

    def test_claude_public_command_has_exact_isolation_and_no_host_paths(self):
        # Resolve host files without reading their contents; no subprocess/inference.
        args = e.claude_command(Path('/work'), 'fable', 'high')
        public = e.public_command(args)
        for flag in ('--restricted', '--strict-mcp-config', '--disable-slash-commands', '--no-session-persistence', '--no-chrome'):
            self.assertIn(flag, public)
        self.assertNotIn('--bare', public)
        self.assertNotIn('--dangerously-skip-permissions', public)
        self.assertNotIn('/'.join(('', 'home', '')), json.dumps(public))
        probe = e.claude_command(Path('/work'), 'fable', 'sin-nivel', True)
        self.assertNotIn('--effort', probe)
        self.assertEqual(probe[probe.index('--tools') + 1], '')

    def test_interrupted_run_is_not_retried(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(e, 'ART', Path(temp)), patch.object(e, 'assert_order'), patch.object(e, 'state', return_value={'estado': 'sondeado', 'niveles': ['low']}), patch.object(e, 'run_one') as call:
            item = e.schedule('fable', 'piloto')[0]
            e.write(Path(temp) / 'fable' / 'iniciadas' / (item['id'] + '.json'), item)
            with self.assertRaisesRegex(RuntimeError, 'sin cierre'):
                e.run_matrix('fable', 'piloto')
            call.assert_not_called()

    def test_quota_blocks_same_provider_but_not_other_provider(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(e, 'ART', Path(temp)), patch.object(e, 'RESULTADOS', Path(temp)):
            e.record_quota('claude-haiku-5-5', 'Rate limit reached')
            self.assertEqual(e.state('claude-opus-5-5')['estado'], 'omitido_cuota')
            self.assertEqual(e.state('fable')['estado'], 'omitido_cuota')
            with self.assertRaisesRegex(RuntimeError, 'cuota'):
                e.assert_order('fable')
            e.assert_order('gpt-6-luna')




class ReviewRegressionTests(unittest.TestCase):
    def response(self, model_id='claude-fable-5-2', **extra):
        return json.dumps({'type': 'result', 'usage': {'input_tokens': 1, 'output_tokens': 1}, 'modelUsage': {model_id: {'inputTokens': 1}}, **extra}).encode()

    def invoke(self, out, err=b'', model='fable'):
        with patch.object(e, 'command', return_value=['official-cli']), patch.object(e.medir, 'run_process', return_value=(0, False, 1, out, err)):
            return e.invoke(Path('/work'), model, 'max', True)

    def test_effort_warning_with_successful_return_is_not_accepted(self):
        message = 'Effort max is not available for this model'
        self.assertEqual(e.category(message), 'nivel_no_admitido')
        result, _ = self.invoke(self.response(), message.encode())
        self.assertEqual(result['error'], 'nivel_no_admitido')
        self.assertEqual(result['error_textual'], message)

    def test_requested_model_is_verified_not_substituted(self):
        for requested in ('fable', 'claude-opus-5-5'):
            result, _ = self.invoke(self.response('claude-haiku-5-5'), model=requested)
            self.assertEqual(result['error'], 'modelo_distinto_del_solicitado')
        result, _ = self.invoke(self.response('claude-fable-5-2-20261001'))
        self.assertEqual(result['error'], '')

    def test_auxiliary_usage_does_not_establish_principal_identity(self):
        mixed = {'claude-haiku-5-5': {'inputTokens': 1}, 'claude-fable-5-2': {'inputTokens': 100}}
        result, _ = self.invoke(self.response(modelUsage=mixed))
        self.assertEqual(result['error'], 'identificador_no_verificable')
        result, _ = self.invoke(self.response(modelUsage=mixed, model='claude-fable-5-2'))
        self.assertEqual(result['error'], '')

    def test_permission_denial_is_infrastructure_and_private_input_not_saved(self):
        result, receipt = self.invoke(self.response(permission_denials=[{'tool_name': 'Edit', 'tool_input': {'private': 'SECRET'}}, {'tool_name': 'Bash'}]))
        self.assertEqual(result['error'], 'permisos_incompatibles')
        self.assertEqual(receipt['permisos_denegados']['herramientas'], ['Bash', 'Edit'])
        self.assertNotIn('SECRET', json.dumps(receipt))

    def test_quota_takes_precedence_over_infrastructure_in_same_batch(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(e, 'ART', Path(temp)), patch.object(e, 'RESULTADOS', Path(temp)), patch.object(e, 'assert_order'), patch.object(e, 'state', return_value={'estado': 'piloto', 'niveles': ['low']}), patch.object(e, 'schedule', return_value=[{'id': 'one'}, {'id': 'two'}]), patch.object(e, 'export', return_value=[{'estado': 'completa', 'tokens_totales': 1}]), patch.object(e, 'save_state'), patch.object(e, 'record_quota') as quota, patch.object(e, 'run_one', side_effect=[{'estado': 'infraestructura', 'cuota': 0, 'error': 'network'}, {'estado': 'cuota', 'cuota': 1, 'error': 'cuota', 'error_textual': 'Rate limit'}]):
            e.run_matrix('claude-haiku-5-5', 'principal')
            quota.assert_called_once_with('claude-haiku-5-5', 'Rate limit')



class RecoveredNetworkRegressionTests(unittest.TestCase):
    def sequence(self, message):
        # Exact recorded event ordering: error index18, successful final index24.
        types = ['thread.started', 'turn.started', 'item.completed', 'item.started', 'item.completed', 'item.started', 'item.completed', 'item.started', 'item.completed', 'item.started', 'item.completed', 'item.started', 'item.completed', 'item.completed', 'item.started', 'item.completed', 'item.started', 'item.completed', 'error', 'item.started', 'item.completed', 'item.started', 'item.completed', 'item.completed', 'turn.completed']
        objects = [{'type': t} for t in types]
        objects[18]['message'] = message
        objects[-1]['usage'] = {'input_tokens': 184613, 'cached_input_tokens': 170368, 'output_tokens': 3461, 'reasoning_output_tokens': 1231}
        return '\n'.join(json.dumps(obj) for obj in objects).encode()

    def invoke(self, message, rc=0):
        with patch.object(e, 'command', return_value=['official-cli']), patch.object(e.medir, 'run_process', return_value=(rc, False, 129.09, self.sequence(message), b'')):
            return e.invoke(Path('/work'), 'gpt-6-luna', 'high')

    def test_recovered_connection_preserves_warning_and_usage_without_final_error(self):
        message = 'Reconnecting... 2/5 (stream disconnected before completion: IO error: Connection reset by peer (os error 104))'
        result, receipt = self.invoke(message)
        self.assertEqual(result['error'], '')
        self.assertEqual(result['tokens_totales'], 188074)
        self.assertEqual(receipt['advertencias'], [message])
        self.assertEqual(receipt['tipos_eventos'][-1], 'turn.completed')
        result, _ = self.invoke(message, rc=1)
        self.assertEqual(result['error'], 'infraestructura')

    def test_quota_is_never_ignored_even_if_turn_completed_follows(self):
        result, receipt = self.invoke('Reconnecting... usage limit reached; stream disconnected')
        self.assertEqual(result['error'], 'cuota')
        self.assertEqual(receipt['advertencias'], [])

    def test_effort_warning_is_not_ignored_even_if_turn_completed_follows(self):
        result, _ = self.invoke('Reconnecting... effort max is not available; stream disconnected')
        self.assertEqual(result['error'], 'nivel_no_admitido')


if __name__ == '__main__':
    unittest.main()
