"""Contrato de captura diagnóstica; no ejecuta proveedores."""
import json
import unittest
import diagnosticar_luna02 as d


class DiagnosticTests(unittest.TestCase):
    def test_completed_commands_and_full_final_are_captured_without_tool_output(self):
        final = 'Observación ' * 1200
        events = [
            {'type':'item.started','item':{'type':'command_execution','command':'python3 modulo.py'}},
            {'type':'item.completed','item':{'type':'command_execution','command':'python3 modulo.py','status':'completed','exit_code':0,'aggregated_output':'PRIVATE OUTPUT'}},
            {'type':'item.completed','item':{'type':'agent_message','text':final}},
            {'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':20}},
        ]
        _, receipt, _, _ = d.parse_diagnostic('codex', '\n'.join(json.dumps(v) for v in events).encode())
        captured = receipt['diagnostico']
        self.assertEqual(captured['mensaje_final'], final)
        self.assertEqual(captured['comandos'], [{'comando':'python3 modulo.py','estado':'completed','retorno':0}])
        self.assertNotIn('PRIVATE OUTPUT', json.dumps(receipt))

    def test_new_seed_balanced_diagnostics_excluded_from_principal(self):
        rows = d.schedule()
        self.assertEqual(rows, d.schedule())
        self.assertEqual(len(rows), 6)
        self.assertEqual({r['fase'] for r in rows}, {'diagnostico'})
        for task in ('04-espera','01-lotes','08-cache'):
            self.assertEqual(sum(r['tarea']==task for r in rows), 2)
        self.assertEqual({r['nivel'] for r in rows}, {'low'})

    def test_full_capture_sanitizes_private_material(self):
        address = '@'.join(('person','example.org'))
        root = '/'.join(('', 'home', 'person', 'private'))
        value = d.sanitize_full(address+' '+root+' Bearer secret-test-value')
        for private in (address, root, 'secret-test-value'):
            self.assertNotIn(private, value)


if __name__ == '__main__': unittest.main()
