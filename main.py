"""Command-line interface for Risk Radar"""

import argparse
import json
import os
import sys
from pathlib import Path

from src.risk_radar import RiskRadar
from src.report_formatter import ReportFormatter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Source Code Risk Radar - Comprehensive Code Quality Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory
  python main.py

  # Analyze specific repository
  python main.py --repo-path /path/to/repo

  # Generate HTML dashboard
  python main.py --repo-path /path/to/repo --output-format html

  # Use dummy data (when git not available)
  python main.py --repo-path /path/to/repo --use-dummy-data

  # Custom output directory
  python main.py --repo-path /path/to/repo --output-dir ./my_reports
        """
    )

    parser.add_argument(
        '--repo-path', '-r',
        type=str,
        default='.',
        help='Path to repository to analyze (default: current directory)'
    )
    parser.add_argument(
        '--output-format', '-f',
        type=str,
        choices=['html', 'json', 'csv', 'console'],
        default='console',
        help='Output format (default: console)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='./reports',
        help='Output directory for reports (default: ./reports)'
    )
    parser.add_argument(
        '--use-dummy-data',
        action='store_true',
        help='Use dummy data instead of analyzing real code (for testing)'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration JSON file'
    )
    parser.add_argument(
        '--analysis',
        type=str,
        choices=['git', 'security', 'complexity', 'ml', 'dependencies', 'all'],
        default='all',
        help='Type of analysis to run (default: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Validate repository path
    if not os.path.isdir(args.repo_path):
        print(f"Error: Repository path '{args.repo_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Load configuration
    config = None
    if args.config:
        if not os.path.exists(args.config):
            print(f"Error: Config file '{args.config}' not found", file=sys.stderr)
            sys.exit(1)
        with open(args.config, 'r') as f:
            config = json.load(f)

    # Print banner
    print("\n" + "=" * 70)
    print("SOURCE CODE RISK RADAR - ANALYSIS IN PROGRESS")
    print("=" * 70 + "\n")

    print(f"Repository: {os.path.abspath(args.repo_path)}")
    print(f"Output Format: {args.output_format}")
    print(f"Output Directory: {args.output_dir}")
    if args.use_dummy_data:
        print("Note: Using dummy data (for testing/demo)")
    print()

    try:
        # Run analysis
        print("Initializing Risk Radar analyzer...")
        radar = RiskRadar(
            repo_path=os.path.abspath(args.repo_path),
            config=config,
            use_dummy_data=args.use_dummy_data
        )

        print("Starting comprehensive code analysis...\n")
        report = radar.analyze()

        # Format and output report
        formatter = ReportFormatter(output_dir=args.output_dir)

        if args.output_format == 'console':
            formatter.print_console_report(report)
        elif args.output_format == 'json':
            json_path = formatter.generate_json_report(report)
            print(f"✓ JSON report saved: {json_path}\n")
        elif args.output_format == 'csv':
            csv_path = formatter.generate_csv_report(report)
            if csv_path:
                print(f"✓ CSV report saved: {csv_path}\n")
        elif args.output_format == 'html':
            html_path = formatter.generate_html_dashboard(report)
            print(f"✓ HTML dashboard saved: {html_path}")
            print(f"  Open in browser: file://{os.path.abspath(html_path)}\n")

        print("=" * 70)
        print("Analysis complete!")
        print("=" * 70 + "\n")

        return 0

    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user")
        return 130
    except Exception as e:
        print(f"\nError during analysis: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
