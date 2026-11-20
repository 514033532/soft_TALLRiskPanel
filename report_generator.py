#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TALLRiskPanel 检测报告生成器 (medical test-report style, bilingual zh/en)
========================================================================
Report structure (per CNIPA-independent, clinical-lab style):
  报告编号 / 样本信息 / 检测项目表(16基因: 检测值+方向+参考范围) /
  检测结果(评分/概率/分层/双引擎) / 结果判读 / 备注与声明 / 审核签名区
All computation local; the report is generated locally.
"""
import datetime
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak)

# ---------------- CJK font ----------------
_F = "Helvetica"; _FB = "Helvetica-Bold"
def _register_fonts():
    """Primary: STSong-Light CID (ASCII+CJK, works on every platform/viewer).
    Embedded TrueType (msyh on Windows) preferred when available."""
    global _F, _FB
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for path in [r"C:\Windows\Fonts\msyh.ttc",
                 r"C:\Windows\Fonts\simhei.ttf"]:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("CJK", path, subfontIndex=0))
                _F = "CJK"; _FB = "CJK"
                return
            except Exception:
                continue
    try:
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        _F = "STSong-Light"; _FB = "STSong-Light"
    except Exception:
        pass
_register_fonts()

LANG = {
    "zh": {
        "title": "检测报告", "soft": "TALLRiskPanel T-ALL 16基因面板风险分层检测报告",
        "report_no": "报告编号", "sample_info": "一、样本信息", "sample_id": "样本编号",
        "test_date": "检测日期", "cohort": "标准化参考队列", "method": "检测方法",
        "method_v": "16基因表达面板 + 双引擎（线性质心 0.594 / 梯度提升决策树 0.442）",
        "items": "二、检测项目与检测值", "gene": "检测基因", "value": "检测值 log2(FPKM+1)",
        "direction": "方向", "ref_range": "参考范围（均值±SD）", "dir_stem": "干样（高危方向）",
        "dir_mature": "成熟（低危方向）", "result": "三、检测结果", "score": "风险评分",
        "score_ref": "参考阈值 0.594", "prob": "高危概率", "prob_ref": "参考阈值 0.442",
        "tier": "分层结果", "tier_high": "高危簇", "tier_low": "低危簇",
        "engine": "双引擎一致性", "engine_ok": "一致", "engine_flag": "不一致（临界标记）",
        "interp": "四、结果判读", "interp_high": "该样本风险评分≥0.594 或 高危概率≥0.442，分层为高危簇。"
            "建议结合临床特征与微小残留病（MRD）结果，评估强化治疗与密切监测的必要性。",
        "interp_low": "该样本风险评分<0.594 且 高危概率<0.442，分层为低危簇。"
            "建议按标准方案治疗并常规监测。",
        "interp_flag": "注意：该样本两引擎结果不一致（临界标记），提示模型对该样本的判定可靠性有限，强烈建议人工复核。",
        "notes": "五、备注与声明", "note1": "本报告由 TALLRiskPanel 软件在本地计算生成，所有计算在本地完成，数据不上传服务器。",
        "note2": "检测值为 log2(FPKM+1) 变换值；参考范围为所选标准化参考队列的均值±标准差。",
        "note3": "本检测结果供医疗专业人员参考，不构成诊断结论；临床决策请结合患者全面情况。",
        "reviewer": "审核人", "reporter": "检测人", "date_": "日期",
        "summary_title": "批量检测结果汇总", "summary_cols": ["样本编号", "风险评分", "高危概率", "分层结果", "双引擎"],
        "page": "第 %d 页",
    },
    "en": {
        "title": "Test Report", "soft": "TALLRiskPanel T-ALL 16-Gene Panel Risk Stratification Test Report",
        "report_no": "Report No.", "sample_info": "1. Sample Information", "sample_id": "Sample ID",
        "test_date": "Test Date", "cohort": "Reference Cohort", "method": "Method",
        "method_v": "16-gene expression panel + dual engines (linear centroid 0.594 / gradient-boosted trees 0.442)",
        "items": "2. Test Items and Values", "gene": "Gene", "value": "Value log2(FPKM+1)",
        "direction": "Direction", "ref_range": "Reference Range (mean±SD)", "dir_stem": "Stem-like (high-risk)",
        "dir_mature": "Mature (low-risk)", "result": "3. Results", "score": "Risk Score",
        "score_ref": "Threshold 0.594", "prob": "High-risk Probability", "prob_ref": "Threshold 0.442",
        "tier": "Tier", "tier_high": "High-risk", "tier_low": "Low-risk",
        "engine": "Dual-engine", "engine_ok": "Agree", "engine_flag": "Disagree (boundary flag)",
        "interp": "4. Interpretation", "interp_high": "Risk score >= 0.594 or probability >= 0.442: high-risk tier. "
            "Intensified therapy and close monitoring should be considered together with clinical and MRD assessment.",
        "interp_low": "Risk score < 0.594 and probability < 0.442: low-risk tier. "
            "Standard regimen with routine monitoring is suggested.",
        "interp_flag": "Note: dual-engine disagreement (boundary flag) indicates limited reliability for this sample; manual review is strongly advised.",
        "notes": "5. Notes and Disclaimer", "note1": "This report was generated locally by TALLRiskPanel; all computation is local and no data is uploaded.",
        "note2": "Values are log2(FPKM+1) transforms; the reference range is the mean±SD of the selected reference cohort.",
        "note3": "For professional reference only; not a diagnostic conclusion. Clinical decisions must integrate the full clinical picture.",
        "reviewer": "Reviewed by", "reporter": "Reported by", "date_": "Date",
        "summary_title": "Batch Results Summary", "summary_cols": ["Sample", "Risk Score", "Probability", "Tier", "Dual-engine"],
        "page": "Page %d",
    },
}

ACCENT = colors.HexColor("#1D4ED8")
LINE = colors.HexColor("#111827")
GREY = colors.HexColor("#4B5563")
LIGHT = colors.HexColor("#EFF6FF")
FLAG = colors.HexColor("#A16207")


def _gen_report_no():
    return "TR-%s-%04d" % (datetime.datetime.now().strftime("%Y%m%d"),
                          int(datetime.datetime.now().timestamp()) % 10000)


def _p(text, size=9.5, bold=False, color=LINE):
    return Paragraph(text, ParagraphStyle("p", fontName=_FB if bold else _F,
                                          fontSize=size, leading=size * 1.45, textColor=color))


def generate_report(results, cohort, lang="zh", path="report.pdf", report_no=None):
    """results: list of dict(sample, score, prob, lin, hgb, agree, genes: {gene: value(log2(x+1))})"""
    T = LANG.get(lang, LANG["zh"])
    report_no = report_no or _gen_report_no()
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=18*mm, bottomMargin=16*mm)
    story = []

    def header(title_line):
        tbl = Table([[Paragraph(f"<b>{T['soft']}</b>", ParagraphStyle(
            "h", fontName=_FB, fontSize=13, leading=16, textColor=colors.white)),
            Paragraph(f"<b>{T['title']}</b>", ParagraphStyle(
                "h2", fontName=_FB, fontSize=13, leading=16, textColor=colors.white, alignment=2))]],
            colWidths=[130*mm, 46*mm])
        tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT),
                                 ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("TOPPADDING", (0, 0), (-1, -1), 8),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
        story.append(tbl)
        story.append(Spacer(1, 3*mm))
        meta_line = "%s: %s    |    %s: %s" % (T['report_no'], report_no, T['test_date'],
                                               datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        story.append(Table([[Paragraph(meta_line, ParagraphStyle(
            "meta", fontName=_F, fontSize=8.5, leading=11, textColor=GREY))]],
            colWidths=[176*mm]))
        story.append(Spacer(1, 4*mm))

    tier_high_vals = {"high", "High", "High-risk", "高危", "高危簇"}

    def sample_block(r, idx):
        # 一、样本信息
        story.append(_p(f"<b>{T['sample_info']}</b>", 10.5, bold=True))
        info = [[_p(T["sample_id"], 9, bold=True), r["sample"] or "-",
                 _p(T["cohort"], 9, bold=True), cohort,
                 _p(T["method"], 9, bold=True), _p(T["method_v"], 9)]]
        t = Table(info, colWidths=[24*mm, 52*mm, 28*mm, 22*mm, 22*mm, 28*mm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.6, LINE),
                               ("BACKGROUND", (0, 0), (0, -1), LIGHT),
                               ("BACKGROUND", (2, 0), (2, -1), LIGHT),
                               ("BACKGROUND", (4, 0), (4, -1), LIGHT),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("TOPPADDING", (0, 0), (-1, -1), 4),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story.append(t)
        story.append(Spacer(1, 4*mm))

        # 二、检测项目与检测值
        story.append(_p(f"<b>{T['items']}</b>", 10.5, bold=True))
        rows = [[_p(T["gene"], 8.5, bold=True), _p(T["value"], 8.5, bold=True),
                 _p(T["direction"], 8.5, bold=True), _p(T["ref_range"], 8.5, bold=True)]]
        for g, meta in r.get("genes", {}).items():
            d = meta.get("direction", "up")
            d_label = T["dir_stem"] if d == "up" else T["dir_mature"]
            rows.append([_p(g, 9), _p(f"{meta['value']:.3f}", 9),
                         _p(d_label, 9), _p(meta["ref_range"], 9)])
        t = Table(rows, colWidths=[26*mm, 34*mm, 40*mm, 76*mm], repeatRows=1)
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, LINE),
                               ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
        story.append(t)
        story.append(Spacer(1, 4*mm))

        # 三、检测结果
        story.append(_p(f"<b>{T['result']}</b>", 10.5, bold=True))
        is_high = str(r["lin"]) in tier_high_vals
        tier_disp = T["tier_high"] if is_high else T["tier_low"]
        tier_c = colors.HexColor("#991B1B") if is_high else colors.HexColor("#166534")
        agree = T["engine_ok"] if r["agree"] != "flag" else T["engine_flag"]
        res = [[_p(T["score"], 9, bold=True), f"{r['score']:.4f}", _p(T["score_ref"], 8.5, color=GREY),
                _p(T["prob"], 9, bold=True), f"{r['prob']:.4f}", _p(T["prob_ref"], 8.5, color=GREY)],
               [_p(T["tier"], 9, bold=True), _p(f"<b>{tier_disp}</b>", 10, color=tier_c), "",
                _p(T["engine"], 9, bold=True), _p(agree, 9, color=FLAG if r["agree"] == "flag" else LINE), ""]]
        t = Table(res, colWidths=[26*mm, 30*mm, 32*mm, 26*mm, 30*mm, 32*mm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, LINE),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("TOPPADDING", (0, 0), (-1, -1), 4),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story.append(t)
        story.append(Spacer(1, 4*mm))

        # 四、结果判读
        story.append(_p(f"<b>{T['interp']}</b>", 10.5, bold=True))
        interp = T["interp_high"] if is_high else T["interp_low"]
        story.append(_p(interp, 9.5))
        if r["agree"] == "flag":
            story.append(_p(f"<b>{T['interp_flag']}</b>", 9.5, color=FLAG))
        story.append(Spacer(1, 4*mm))

    # header
    header(T["title"])

    # 五、备注与声明 (as summary block, placed after all sample blocks or before)
    def notes():
        story.append(_p(f"<b>{T['notes']}</b>", 10.5, bold=True))
        for n in ["note1", "note2", "note3"]:
            story.append(_p(T[n], 9, color=GREY))
        story.append(Spacer(1, 6*mm))
        story.append(Table([[_p(T["reporter"] + ": ______________", 9),
                             _p(T["reviewer"] + ": ______________", 9),
                             _p(T["date_"] + ": ______________", 9)]],
                          colWidths=[60*mm, 60*mm, 56*mm]))
        story.append(Spacer(1, 2*mm))
        story.append(_p("Han Zhang · Dongguan Hospital Affiliated to Shenzhen University, "
                        "Dongguan 523120, Guangdong, China · zhangh355@mail2.sysu.edu.cn",
                        7.5, color=GREY))

    if len(results) > 1:
        story.append(_p(f"<b>{T['summary_title']}</b>", 10.5, bold=True))
        rows = [[_p(c, 8.5, bold=True) for c in T["summary_cols"]]]
        for r in results:
            th = str(r["lin"]) in tier_high_vals
            rows.append([_p(str(r["sample"]), 9), _p(f"{r['score']:.4f}", 9),
                         _p(f"{r['prob']:.4f}", 9), _p(T["tier_high"] if th else T["tier_low"], 9),
                         _p(T["engine_ok"] if r["agree"] != "flag" else T["engine_flag"], 9)])
        t = Table(rows, colWidths=[36*mm, 30*mm, 30*mm, 40*mm, 40*mm], repeatRows=1)
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, LINE),
                               ("BACKGROUND", (0, 0), (-1, 0), LIGHT)]))
        story.append(t)
        story.append(Spacer(1, 5*mm))

    for i, r in enumerate(results):
        if i > 0:
            story.append(PageBreak())
        sample_block(r, i)

    notes()

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont(_F, 7.5)
        canvas.setFillColor(GREY)
        canvas.drawString(18*mm, 9*mm, T["soft"])
        canvas.drawRightString(A4[0]-18*mm, 9*mm, T["page"] % canvas.getPageNumber())
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return path
