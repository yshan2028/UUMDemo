#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: visualize_results.py
Author: yshan2028
Created: 2025-06-13 08:54:05
Description: 数据可视化工具
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import logging
from config.settings import RESULTS_PATH

logger = logging.getLogger(__name__)


def visualize_performance_comparison(comparison_results):
    """可视化性能对比结果"""
    try:
        # 创建性能对比图表
        systems = ['DVSS-PPA', 'Hyperledger', 'Ethereum']
        latencies = [
            comparison_results["dvss_ppa_results"]["avg_latency_ms"],
            comparison_results["hyperledger_simulation"]["avg_latency_ms"],
            comparison_results["ethereum_simulation"]["avg_latency_ms"]
        ]
        throughputs = [
            comparison_results["dvss_ppa_results"]["avg_throughput_tps"],
            comparison_results["hyperledger_simulation"]["avg_throughput_tps"],
            comparison_results["ethereum_simulation"]["avg_throughput_tps"]
        ]

        # 延迟对比图
        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        bars1 = plt.bar(systems, latencies, color=['#2E8B57', '#4682B4', '#CD853F'])
        plt.title('Average Latency Comparison')
        plt.ylabel('Latency (ms)')
        plt.yscale('log')  # 使用对数刻度

        # 添加数值标签
        for bar, latency in zip(bars1, latencies):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                     f'{latency:.1f}ms', ha='center', va='bottom')

        # 吞吐量对比图
        plt.subplot(1, 2, 2)
        bars2 = plt.bar(systems, throughputs, color=['#2E8B57', '#4682B4', '#CD853F'])
        plt.title('Average Throughput Comparison')
        plt.ylabel('Throughput (TPS)')

        # 添加数值标签
        for bar, throughput in zip(bars2, throughputs):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                     f'{throughput:.1f}', ha='center', va='bottom')

        plt.tight_layout()

        # 保存图表
        chart_path = os.path.join(RESULTS_PATH, "performance_comparison.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Performance comparison chart saved to: {chart_path}")
        return chart_path

    except Exception as e:
        logger.error(f"Failed to create performance comparison chart: {e}")
        return None


def visualize_privacy_scores(privacy_results):
    """可视化隐私保护评分"""
    try:
        scores = privacy_results["privacy_scores"]
        categories = ['Access Control', 'Secret Sharing', 'Zero Knowledge', 'Overall']
        values = [
            scores["access_control_score"],
            scores["secret_sharing_score"],
            scores["zero_knowledge_score"],
            scores["overall_privacy_score"]
        ]

        plt.figure(figsize=(10, 6))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        bars = plt.bar(categories, values, color=colors)

        plt.title('Privacy Protection Scores')
        plt.ylabel('Score (%)')
        plt.ylim(0, 100)

        # 添加数值标签
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f'{value:.1f}%', ha='center', va='bottom')

        # 添加及格线
        plt.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='Target (80%)')
        plt.legend()

        plt.tight_layout()

        # 保存图表
        chart_path = os.path.join(RESULTS_PATH, "privacy_scores.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Privacy scores chart saved to: {chart_path}")
        return chart_path

    except Exception as e:
        logger.error(f"Failed to create privacy scores chart: {e}")
        return None


def visualize_throughput_scalability(throughput_results):
    """可视化吞吐量可扩展性"""
    try:
        multi_thread_results = throughput_results["multi_thread_results"]

        thread_counts = []
        tps_values = []

        for key, result in multi_thread_results.items():
            thread_counts.append(result["thread_count"])
            tps_values.append(result["transactions_per_second"])

        # 排序确保线性显示
        sorted_data = sorted(zip(thread_counts, tps_values))
        thread_counts, tps_values = zip(*sorted_data)

        plt.figure(figsize=(10, 6))
        plt.plot(thread_counts, tps_values, 'o-', linewidth=2, markersize=8, color='#3498db')

        # 理想线性扩展线
        single_thread_tps = throughput_results["single_thread_results"]["transactions_per_second"]
        ideal_tps = [single_thread_tps * tc for tc in thread_counts]
        plt.plot(thread_counts, ideal_tps, '--', alpha=0.7, color='red', label='Ideal Linear Scaling')

        plt.title('Throughput Scalability Analysis')
        plt.xlabel('Number of Threads')
        plt.ylabel('Throughput (TPS)')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 添加数值标签
        for tc, tps in zip(thread_counts, tps_values):
            plt.annotate(f'{tps:.1f}', (tc, tps), textcoords="offset points",
                         xytext=(0, 10), ha='center')

        plt.tight_layout()

        # 保存图表
        chart_path = os.path.join(RESULTS_PATH, "throughput_scalability.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Throughput scalability chart saved to: {chart_path}")
        return chart_path

    except Exception as e:
        logger.error(f"Failed to create throughput scalability chart: {e}")
        return None


def generate_all_visualizations(experiment_results):
    """生成所有可视化图表"""
    chart_paths = []

    if 'comparison' in experiment_results:
        chart_path = visualize_performance_comparison(experiment_results['comparison'])
        if chart_path:
            chart_paths.append(chart_path)

    if 'privacy' in experiment_results:
        chart_path = visualize_privacy_scores(experiment_results['privacy'])
        if chart_path:
            chart_paths.append(chart_path)

    # 如果有吞吐量测试结果，添加可视化
    for key, results in experiment_results.items():
        if 'throughput' in key.lower() and 'multi_thread_results' in results:
            chart_path = visualize_throughput_scalability(results)
            if chart_path:
                chart_paths.append(chart_path)
            break

    logger.info(f"Generated {len(chart_paths)} visualization charts")
    return chart_paths