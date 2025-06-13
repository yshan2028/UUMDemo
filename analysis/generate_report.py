#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: generate_report.py
Author: yshan2028
Created: 2025-06-13 08:54:05
Description: 生成实验报告
"""

import os
import json
import logging
from datetime import datetime
from config.settings import RESULTS_PATH
from analysis.visualize_results import generate_all_visualizations

logger = logging.getLogger(__name__)


def generate_comprehensive_report(experiment_results):
    """生成综合实验报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(RESULTS_PATH, f"experiment_report_{timestamp}.html")

    try:
        # 生成可视化图表
        chart_paths = generate_all_visualizations(experiment_results)

        # 生成HTML报告
        html_content = _generate_html_report(experiment_results, chart_paths, timestamp)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 同时生成JSON格式的详细结果
        json_path = os.path.join(RESULTS_PATH, f"experiment_results_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(experiment_results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Comprehensive report generated: {report_path}")
        logger.info(f"Detailed JSON results saved: {json_path}")

        return report_path

    except Exception as e:
        logger.error(f"Failed to generate comprehensive report: {e}")
        return None


def _generate_html_report(experiment_results, chart_paths, timestamp):
    """生成HTML格式报告"""

    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVSS-PPA Experiment Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        .metric-box {{
            background: #ecf0f1;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .highlight {{
            background: #e8f5e8;
            color: #27ae60;
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: bold;
        }}
        .warning {{
            background: #fdf2e9;
            color: #e67e22;
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: bold;
        }}
        .error {{
            background: #fadbd8;
            color: #e74c3c;
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .chart-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>DVSS-PPA Blockchain Privacy Protection Experiment Report</h1>

        <div class="metric-box">
            <strong>Report Generated:</strong> {report_time}<br>
            <strong>Experimenter:</strong> yshan2028<br>
            <strong>System:</strong> Dynamic Verifiable Secret Sharing with Privacy-Preserving Access (DVSS-PPA)
        </div>

        {executive_summary}

        {performance_section}

        {privacy_section}

        {comparison_section}

        {charts_section}

        {conclusions}

        <div class="footer">
            <p>© 2025 yshan2028 - DVSS-PPA Experiment System</p>
            <p>Generated automatically by the DVSS-PPA analysis module</p>
        </div>
    </div>
</body>
</html>
    """

    # 生成各个部分的内容
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    executive_summary = _generate_executive_summary(experiment_results)
    performance_section = _generate_performance_section(experiment_results)
    privacy_section = _generate_privacy_section(experiment_results)
    comparison_section = _generate_comparison_section(experiment_results)
    charts_section = _generate_charts_section(chart_paths)
    conclusions = _generate_conclusions(experiment_results)

    return html_template.format(
        report_time=report_time,
        executive_summary=executive_summary,
        performance_section=performance_section,
        privacy_section=privacy_section,
        comparison_section=comparison_section,
        charts_section=charts_section,
        conclusions=conclusions
    )


def _generate_executive_summary(experiment_results):
    """生成执行摘要"""
    summary = "<h2>Executive Summary</h2>"

    # 统计实验完成情况
    completed_tests = len(experiment_results)
    summary += f"<p>This report presents the results of a comprehensive evaluation of the DVSS-PPA system, "
    summary += f"consisting of <strong>{completed_tests}</strong> major test categories.</p>"

    summary += "<div class='summary-stats'>"

    # 性能指标卡片
    if 'performance' in experiment_results:
        perf_data = experiment_results['performance']
        if 'overall_metrics' in perf_data:
            tps = perf_data['overall_metrics'].get('throughput_tps', 0)
            summary += f"""
            <div class="stat-card">
                <div class="stat-value">{tps:.1f}</div>
                <div>Throughput (TPS)</div>
            </div>
            """

    # 隐私评分卡片
    if 'privacy' in experiment_results:
        privacy_data = experiment_results['privacy']
        if 'privacy_scores' in privacy_data:
            overall_score = privacy_data['privacy_scores'].get('overall_privacy_score', 0)
            summary += f"""
            <div class="stat-card">
                <div class="stat-value">{overall_score:.1f}%</div>
                <div>Privacy Score</div>
            </div>
            """

    # 对比改进卡片
    if 'comparison' in experiment_results:
        comp_data = experiment_results['comparison']
        if 'comparison_metrics' in comp_data:
            hyperledger_improvement = comp_data['comparison_metrics']['dvss_vs_hyperledger'].get('latency_improvement', 0)
            summary += f"""
            <div class="stat-card">
                <div class="stat-value">{hyperledger_improvement:.1f}%</div>
                <div>Latency Improvement vs Hyperledger</div>
            </div>
            """

    summary += "</div>"

    return summary


def _generate_performance_section(experiment_results):
    """生成性能测试部分"""
    if 'performance' not in experiment_results:
        return ""

    section = "<h2>Performance Analysis</h2>"
    perf_data = experiment_results['performance']

    if 'algorithm_performance' in perf_data:
        section += "<h3>Algorithm Performance</h3>"
        algo_perf = perf_data['algorithm_performance']

        if 'shamir' in algo_perf:
            shamir_metrics = algo_perf['shamir']
            section += f"""
            <div class="metric-box">
                <strong>Shamir Secret Sharing Performance:</strong><br>
                Average Time: <span class="highlight">{shamir_metrics.get('avg', 0):.2f} ms</span><br>
                Min Time: {shamir_metrics.get('min', 0):.2f} ms<br>
                Max Time: {shamir_metrics.get('max', 0):.2f} ms<br>
                Operations: {shamir_metrics.get('count', 0)}
            </div>
            """

    if 'overall_metrics' in perf_data:
        overall = perf_data['overall_metrics']
        section += f"""
        <h3>Overall System Performance</h3>
        <div class="metric-box">
            <strong>System-wide Metrics:</strong><br>
            Total Orders Processed: <span class="highlight">{overall.get('total_orders_processed', 0)}</span><br>
            Average Processing Time: {overall.get('avg_processing_time', 0):.2f} ms<br>
            System Throughput: <span class="highlight">{overall.get('throughput_tps', 0):.2f} TPS</span>
        </div>
        """

    return section


def _generate_privacy_section(experiment_results):
    """生成隐私保护部分"""
    if 'privacy' not in experiment_results:
        return ""

    section = "<h2>Privacy Protection Analysis</h2>"
    privacy_data = experiment_results['privacy']

    if 'privacy_scores' in privacy_data:
        scores = privacy_data['privacy_scores']
        section += """
        <h3>Privacy Protection Scores</h3>
        <table>
            <tr>
                <th>Component</th>
                <th>Score</th>
                <th>Status</th>
            </tr>
        """

        components = [
            ("Access Control", scores.get('access_control_score', 0)),
            ("Secret Sharing", scores.get('secret_sharing_score', 0)),
            ("Zero Knowledge Proof", scores.get('zero_knowledge_score', 0)),
            ("Overall Privacy", scores.get('overall_privacy_score', 0))
        ]

        for name, score in components:
            status_class = "highlight" if score >= 80 else "warning" if score >= 60 else "error"
            status_text = "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Improvement"

            section += f"""
            <tr>
                <td>{name}</td>
                <td><span class="{status_class}">{score:.1f}%</span></td>
                <td>{status_text}</td>
            </tr>
            """

        section += "</table>"

    return section


def _generate_comparison_section(experiment_results):
    """生成对比分析部分"""
    if 'comparison' not in experiment_results:
        return ""

    section = "<h2>Comparative Analysis</h2>"
    comp_data = experiment_results['comparison']

    # 性能对比表
    section += "<h3>System Performance Comparison</h3>"
    section += """
    <table>
        <tr>
            <th>System</th>
            <th>Avg Latency (ms)</th>
            <th>Avg Throughput (TPS)</th>
            <th>Performance Rating</th>
        </tr>
    """

    systems = [
        ("DVSS-PPA", comp_data.get('dvss_ppa_results', {})),
        ("Hyperledger", comp_data.get('hyperledger_simulation', {})),
        ("Ethereum", comp_data.get('ethereum_simulation', {}))
    ]

    for name, metrics in systems:
        latency = metrics.get('avg_latency_ms', 0)
        throughput = metrics.get('avg_throughput_tps', 0)

        # 基于延迟评定性能等级
        if latency < 100:
            rating = '<span class="highlight">Excellent</span>'
        elif latency < 500:
            rating = '<span class="warning">Good</span>'
        else:
            rating = '<span class="error">Fair</span>'

        section += f"""
        <tr>
            <td><strong>{name}</strong></td>
            <td>{latency:.1f}</td>
            <td>{throughput:.1f}</td>
            <td>{rating}</td>
        </tr>
        """

    section += "</table>"

    # 改进百分比
    if 'comparison_metrics' in comp_data:
        metrics = comp_data['comparison_metrics']
        section += "<h3>Improvement Analysis</h3>"

        hyperledger_latency = metrics['dvss_vs_hyperledger'].get('latency_improvement', 0)
        ethereum_latency = metrics['dvss_vs_ethereum'].get('latency_improvement', 0)

        section += f"""
        <div class="metric-box">
            <strong>DVSS-PPA Performance Improvements:</strong><br>
            vs Hyperledger: <span class="highlight">{hyperledger_latency:.1f}% latency reduction</span><br>
            vs Ethereum: <span class="highlight">{ethereum_latency:.1f}% latency reduction</span>
        </div>
        """

    return section


def _generate_charts_section(chart_paths):
    """生成图表部分"""
    if not chart_paths:
        return ""

    section = "<h2>Visualization Charts</h2>"

    for chart_path in chart_paths:
        chart_name = os.path.basename(chart_path)
        # 使用相对路径
        relative_path = chart_name

        section += f"""
        <div class="chart-container">
            <h3>{chart_name.replace('_', ' ').replace('.png', '').title()}</h3>
            <img src="{relative_path}" alt="{chart_name}">
        </div>
        """

    return section


def _generate_conclusions(experiment_results):
    """生成结论部分"""
    conclusions = "<h2>Conclusions and Recommendations</h2>"

    conclusions += "<h3>Key Findings</h3>"
    conclusions += "<ul>"

    # 基于实验结果生成结论
    if 'performance' in experiment_results:
        perf_data = experiment_results['performance']
        if 'overall_metrics' in perf_data:
            tps = perf_data['overall_metrics'].get('throughput_tps', 0)
            if tps > 1000:
                conclusions += "<li>✅ System demonstrates <strong>high throughput performance</strong> suitable for enterprise applications</li>"
            else:
                conclusions += "<li>⚠️ System throughput may require optimization for high-load scenarios</li>"

    if 'privacy' in experiment_results:
        privacy_data = experiment_results['privacy']
        if 'privacy_scores' in privacy_data:
            overall_score = privacy_data['privacy_scores'].get('overall_privacy_score', 0)
            if overall_score >= 80:
                conclusions += "<li>✅ <strong>Excellent privacy protection</strong> across all evaluated components</li>"
            elif overall_score >= 60:
                conclusions += "<li>⚠️ Good privacy protection with room for improvement in some areas</li>"
            else:
                conclusions += "<li>❌ Privacy protection mechanisms require significant enhancement</li>"

    if 'comparison' in experiment_results:
        comp_data = experiment_results['comparison']
        if 'comparison_metrics' in comp_data:
            improvement = comp_data['comparison_metrics']['dvss_vs_hyperledger'].get('latency_improvement', 0)
            if improvement > 50:
                conclusions += "<li>✅ <strong>Significant performance advantages</strong> over existing blockchain solutions</li>"
            elif improvement > 0:
                conclusions += "<li>✅ Measurable performance improvements over traditional approaches</li>"

    conclusions += "</ul>"

    conclusions += "<h3>Recommendations</h3>"
    conclusions += "<ul>"
    conclusions += "<li>Continue monitoring system performance under varying load conditions</li>"
    conclusions += "<li>Implement additional security hardening measures based on attack simulation results</li>"
    conclusions += "<li>Consider deployment in production environments for real-world validation</li>"
    conclusions += "<li>Explore integration with additional blockchain platforms</li>"
    conclusions += "</ul>"

    return conclusions