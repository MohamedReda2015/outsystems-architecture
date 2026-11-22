"""Behavioral CLI parity tests. Run with Python; set OUTSYSTEMS_NODE if needed."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = os.environ.get('OUTSYSTEMS_NODE') or shutil.which('node')


class ValidatorTests(unittest.TestCase):
    def run_pair(self, data, strict=False, expected_code=None):
        self.assertTrue(NODE, 'Node.js is required; set OUTSYSTEMS_NODE')
        with tempfile.TemporaryDirectory(prefix='os-architecture-test-') as tmp:
            file = Path(tmp)/'graph.json'
            file.write_text(json.dumps(data), encoding='utf-8')
            args = [str(file), '--json'] + (['--strict'] if strict else [])
            results = [subprocess.run([exe, str(ROOT/'scripts'/script), *args], capture_output=True, text=True, encoding='utf-8')
                       for exe, script in [(sys.executable, 'validate_architecture.py'), (NODE, 'validate_architecture.mjs')]]
        self.assertEqual(results[0].returncode, results[1].returncode, [r.stderr for r in results])
        if expected_code is not None:
            self.assertEqual(results[0].returncode, expected_code, [r.stderr or r.stdout for r in results])
        if results[0].returncode == 2:
            self.assertTrue(all(r.stderr.strip() for r in results))
            return None
        outputs = [json.loads(r.stdout) for r in results]
        self.assertEqual(outputs[0], outputs[1])
        return outputs[0]

    def test_legacy_fixtures(self):
        for file, code in [('example_deps.json', 0), ('example_deps_bad.json', 1)]:
            with self.subTest(file=file):
                self.run_pair(json.loads((ROOT/'scripts'/file).read_text(encoding='utf-8')), True, code)

    def test_weak_destinations_do_not_make_canvas_cycles(self):
        modules=[{'name':'Alpha_Portal','app':'Alpha','references':[{'target':'Beta_Portal','kind':'screen-destination'}]},
                 {'name':'Beta_Portal','app':'Beta','references':[{'target':'Alpha_Portal','kind':'screen-destination'}]}]
        for strict in [False, True]:
            r=self.run_pair({'modules':modules}, strict, 0)
            self.assertEqual(r['findings'], [])
            self.assertEqual(r['summary']['reference_counts']['weak'], 2)

    def test_strong_side_reference_and_cycle_remain_findings(self):
        r=self.run_pair({'modules':[{'name':'Alpha_FE','app':'A','references':['Beta_FE']}, {'name':'Beta_FE','app':'B','references':['Alpha_FE']}]}, expected_code=1)
        self.assertTrue({'ARC-02','ARC-03','ARC-04'}.issubset({f['rule'] for f in r['findings']}))

    def test_mixed_pair_does_not_hide_strong_reference(self):
        r=self.run_pair({'modules':[{'name':'Alpha_FE','references':[{'target':'Beta_FE','kind':'screen-destination'},'Beta_FE']},{'name':'Beta_FE'}]},expected_code=1)
        self.assertIn('ARC-02',[f['rule'] for f in r['findings']])

    def test_strict_house_rule_is_separate_from_canvas(self):
        data={'modules':[{'name':'Orders_FE','references':[{'target':'Orders_BL','kind':'service-action'}]},{'name':'Orders_BL'}]}
        self.run_pair(data,False,0)
        r=self.run_pair(data,True,1)
        self.assertEqual([f['rule'] for f in r['findings']],['HSE-03'])

    def test_unknown_and_external_evidence(self):
        r=self.run_pair({'modules':[{'name':'Orders_CS','references':[{'target':'Orders_BL','kind':'unknown'},'External']},{'name':'Orders_BL'}]},expected_code=1)
        self.assertFalse(r['summary']['validation_complete'])
        self.assertEqual(r['summary']['external_modules'],['External'])
        self.assertIn('ARC-10',[f['rule'] for f in r['findings']])

    def test_empty_inventory_is_not_complete(self):
        r=self.run_pair({'modules':[]},expected_code=0)
        self.assertFalse(r['summary']['validation_complete'])
        self.assertTrue(r['findings'])

    def test_explicit_layer_avoids_suffix_guess(self):
        r=self.run_pair({'modules':[{'name':'Catalog','layer':'core'}]},expected_code=0)
        self.assertEqual(r['summary']['layers']['Catalog'],'core')
        self.assertEqual(r['findings'],[])

    def test_explicit_roles_drive_sublayer_validation(self):
        r=self.run_pair({'modules':[{'name':'Storage','layer':'core','role':'cs','references':['Logic']},{'name':'Logic','layer':'core','role':'bl'}]},expected_code=1)
        self.assertIn('ARC-10',[f['rule'] for f in r['findings']])

    def test_workflow_modules_are_core(self):
        r=self.run_pair({'modules':[{'name':'Orders_WF','references':['Orders_BL']},{'name':'Orders_BPT'},{'name':'Orders_BL'}]},expected_code=0)
        self.assertEqual(set(r['summary']['layers'].values()),{'core'})

    def test_bad_inputs_are_usage_errors(self):
        bad=[None,{}, {'modules':None}, {'modules':[None]}, {'modules':[{'name':''}]},
             {'modules':[{'name':'A_CS'},{'name':'A_CS'}]}, {'modules':[{'name':'A_CS','references':'B_CS'}]},
             {'modules':[{'name':'A_CS','references':[{'target':'B_CS','kind':'typo'}]}]},
             {'modules':[{'name':'A_CS','references':[None]}]}, {'modules':[{'name':'A_CS','role':None}]},
             {'modules':[{'name':'A_CS','layer':None}]}]
        for data in bad:
            with self.subTest(data=data): self.run_pair(data,expected_code=2)


if __name__=='__main__': unittest.main()
