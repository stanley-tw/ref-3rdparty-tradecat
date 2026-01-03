# -*- coding: utf-8 -*-
"""
AI 分析管道
- 获取全量数据 -> 精简为 LLM 可处理大小 -> 构建提示词 -> 调用 LLM -> 保存结果
"""
from __future__ import annotations

import asyncio
import json
from typing import Dict, Any, List

from src.data import fetch_payload
from src.prompt import build_prompt
from src.llm import call_llm
from src.utils.run_recorder import RunRecorder


def _slim_payload(payload: Dict[str, Any], interval: str) -> Dict[str, Any]:
    """
    精简 payload 为 LLM 可处理大小（约 50-100KB）
    保留关键数据，去除冗余
    """
    # 周期映射：请求周期 + 相邻大周期
    interval_map = {
        "1m": ["1m", "5m"],
        "5m": ["5m", "15m"],
        "15m": ["15m", "1h"],
        "1h": ["1h", "4h"],
        "4h": ["4h", "1d"],
        "1d": ["1d", "1w"],
        "1w": ["1w"],
    }
    target_intervals = interval_map.get(interval, [interval])
    
    slim = {
        "symbol": payload.get("symbol"),
        "interval": interval,
        "generated_at": payload.get("generated_at"),
    }
    
    # K线：只保留目标周期，每个最多 30 条
    candles = payload.get("candles", {})
    slim["candles"] = {}
    for iv in target_intervals:
        if iv in candles:
            slim["candles"][iv] = candles[iv][:30]
    
    # 期货指标：最多 20 条
    slim["metrics"] = payload.get("metrics", [])[:20]
    
    # SQLite 指标：只保留目标周期的数据
    indicators = payload.get("indicators", {})
    slim["indicators"] = {}
    for tbl, data in indicators.items():
        if isinstance(data, list):
            # 过滤出目标周期
            filtered = [r for r in data if r.get("周期") in target_intervals]
            if filtered:
                slim["indicators"][tbl] = filtered[:5]  # 每表最多 5 条
        elif isinstance(data, dict) and "error" not in data:
            slim["indicators"][tbl] = data
    
    # 单币快照：只保留目标周期
    snapshot = payload.get("snapshot", {})
    slim["snapshot"] = {}
    for panel, tables in snapshot.items():
        slim["snapshot"][panel] = {}
        for tbl, periods in tables.items():
            if isinstance(periods, dict):
                filtered = {p: v for p, v in periods.items() if p in target_intervals}
                if filtered:
                    slim["snapshot"][panel][tbl] = filtered
    
    return slim


async def run_analysis(symbol: str, interval: str, prompt_name: str) -> Dict[str, Any]:
    """
    执行 AI 分析
    
    Args:
        symbol: 交易对，如 BTCUSDT
        interval: 时间周期，如 1h
        prompt_name: 提示词名称
        
    Returns:
        分析结果字典
    """
    # 1. 获取全量数据
    payload = await asyncio.to_thread(fetch_payload, symbol, interval)

    # 2. 精简数据（控制在 LLM 可处理范围）
    slim_payload = _slim_payload(payload, interval)

    # 3. 构建提示词
    system_prompt, data_json = await asyncio.to_thread(build_prompt, prompt_name, slim_payload)
    
    user_content = (
        "请基于以下交易数据进行市场分析，输出中文结论\n"
        "禁止原样粘贴 DATA_JSON 或长表格；只输出摘要和关键数值\n"
        "===DATA_JSON===\n"
        f"{data_json}"
    )

    # 4. 调用 LLM
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    analysis_text, raw_response = await call_llm(messages)

    # 5. 保存结果（保存全量 payload 用于调试）
    recorder = RunRecorder()
    await asyncio.to_thread(
        recorder.save_run,
        symbol,
        interval,
        prompt_name,
        payload,  # 保存全量数据
        system_prompt,
        analysis_text,
        messages,
    )

    return {
        "analysis": analysis_text,
        "raw_response": raw_response,
        "payload": payload,
    }


__all__ = ["run_analysis"]
