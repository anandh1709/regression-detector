def generate_html_report(run_data, baseline, comparison_results, regressions):
    scorecard_rows = ""
    for r in comparison_results:
        scorecard_rows += f"""
        <tr>
            <td>{r['metric']}</td>
            <td>{r['delta']}</td>
            <td>{r['severity']}</td>
            <td class="{r['status']}">{r['status']}</td>
        </tr>
        """

    if regressions:
        regression_rows = ""
        for reg in regressions:
            regression_rows += f"""
            <tr>
                <td>{reg['id']}</td>
                <td>{reg['email_expected_category']}</td>
                <td>{reg['baseline_actual_category']}</td>
                <td>{reg['new_actual_category']}</td>
            </tr>
            """
    else:
        regression_rows = "<tr><td colspan='4'>No regressed cases</td></tr>"

    html = f"""
    <html>
    <head>
        <title>Eval Report - {run_data['timestamp']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            .fine {{ color: green; }}
            .warning {{ color: orange; font-weight: bold; }}
            .critical {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Regression Eval Report</h1>
        <p><b>Run timestamp:</b> {run_data['timestamp']}</p>
        <p><b>Prompt version:</b> {run_data['prompt_version']}</p>
        <p><b>Baseline timestamp:</b> {baseline['timestamp']}</p>

        <h2>Scorecard vs Baseline</h2>
        <table>
            <tr><th>Metric</th><th>Delta</th><th>Severity</th><th>Status</th></tr>
            {scorecard_rows}
        </table>

        <h2>Regressed Cases</h2>
        <table>
            <tr><th>ID</th><th>Expected</th><th>Baseline Got</th><th>New Run Got</th></tr>
            {regression_rows}
        </table>
    </body>
    </html>
    """

    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html)