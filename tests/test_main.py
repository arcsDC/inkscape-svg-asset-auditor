import unittest
import os
import tempfile
import sys

# Add parent directory to path to import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock inkscape extension module if not available
try:
    import inkscape.extension
except ImportError:
    import types
    mock_inkscape = types.ModuleType('inkscape')
    mock_extension = types.ModuleType('inkscape.extension')
    
    class MockExtension:
        def __init__(self):
            import argparse
            self.arg_parser = argparse.ArgumentParser()
            self._errors = []
            self._infos = []
        
        def report_error(self, msg):
            self._errors.append(msg)
        
        def report_info(self, msg):
            self._infos.append(msg)
            
    mock_extension.Extension = MockExtension
    mock_inkscape.extension = mock_extension
    sys.modules['inkscape'] = mock_inkscape
    sys.modules['inkscape.extension'] = mock_extension

import inkscape_svg_asset_auditor

class TestSvgAssetAuditor(unittest.TestCase):
    def setUp(self):
        self.auditor = inkscape_svg_asset_auditor.SvgAssetAuditor()
        
    def test_missing_file(self):
        class Args:
            input_svg = "/nonexistent/file.svg"
            output = None
        self.auditor.run(Args())
        self.assertTrue(any("not found" in e for e in self.auditor._errors))

    def test_valid_svg(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg"><rect id="r1"/></svg>')
            svg_path = f.name
        
        class Args:
            input_svg = svg_path
            output = None
        self.auditor.run(Args())
        self.assertFalse(self.auditor._errors)
        os.unlink(svg_path)

    def test_duplicate_ids(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg"><rect id="dup"/><circle id="dup"/></svg>')
            svg_path = f.name
        
        class Args:
            input_svg = svg_path
            output = None
        self.auditor.run(Args())
        self.assertTrue(any("Duplicate ID" in i for i in self.auditor._infos))
        os.unlink(svg_path)

if __name__ == '__main__':
    unittest.main()
