#!/usr/bin/env python3
import sys
import os
import xml.etree.ElementTree as ET
from inkscape.extension import Extension

class SvgAssetAuditor(Extension):
    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument('--input-svg', type=str, help='Path to SVG file')
        self.arg_parser.add_argument('--output', type=str, help='Output report path')

    def live_update(self, args):
        pass

    def run(self, args):
        if not args.input_svg or not os.path.exists(args.input_svg):
            self.report_error("Input SVG file not found.")
            return

        try:
            tree = ET.parse(args.input_svg)
            root = tree.getroot()
        except ET.ParseError as e:
            self.report_error(f"XML Parse Error: {e}")
            return

        issues = []
        ids_seen = {}
        
        # Check for missing or duplicate IDs
        for elem in root.iter():
            id_val = elem.get('id')
            if id_val is None:
                continue
            if id_val in ids_seen:
                issues.append(f"Duplicate ID: '{id_val}'")
            else:
                ids_seen[id_val] = True

        # Check file size
        file_size = os.path.getsize(args.input_svg)
        if file_size > 5 * 1024 * 1024:
            issues.append(f"File size exceeds 5MB: {file_size} bytes")

        # Check for empty groups
        for g in root.iter():
            if g.tag.endswith('g') and len(list(g)) == 0:
                issues.append(f"Empty group found: '{g.get('id', 'unnamed')}'")

        report_lines = ["SVG Asset Audit Report", "=" * 30]
        if issues:
            report_lines.append(f"Found {len(issues)} issue(s):")
            for issue in issues:
                report_lines.append(f"  - {issue}")
        else:
            report_lines.append("No issues found. Asset is clean.")
        
        report_text = "\n".join(report_lines)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report_text)
            self.report_info(f"Report saved to {args.output}")
        else:
            self.report_info(report_text)

if __name__ == '__main__':
    SvgAssetAuditor().run(sys.argv[1:])
