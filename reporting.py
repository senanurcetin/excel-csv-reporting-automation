"""Create a standalone, offline-friendly HTML report with no external dependencies."""
from __future__ import annotations

from decimal import Decimal
from html import escape


def chart_rows(items: list[dict], name_key: str) -> str:
    maximum = max((Decimal(x["recognized_revenue_usd"]) for x in items), default=Decimal("0"))
    chunks = []
    for x in items:
        value = Decimal(x["recognized_revenue_usd"])
        width = float(value / maximum * 100) if maximum > 0 else 0
        label = escape(str(x[name_key]))
        chunks.append(f'<div class="barrow"><span class="barlabel">{label}</span><span class="bartrack"><span class="barfill" style="width:{width:.1f}%"></span></span><b>${value:,.2f}</b></div>')
    return "\n".join(chunks) if chunks else "<p>No values available.</p>"


def issue_rows(issues: dict[str, int]) -> str:
    if not issues:
        return '<tr><td colspan="2">No issues detected</td></tr>'
    return "\n".join(f"<tr><td>{escape(name.replace('_', ' ').title())}</td><td class='num'>{count}</td></tr>" for name,count in issues.items())


def build_html(data: dict) -> str:
    revenue = Decimal(data["recognized_revenue_usd"])
    refunded = Decimal(data["refunded_order_value_usd"])
    cancelled = Decimal(data["cancelled_order_value_usd"])
    quality_rate = (100 * data["valid_rows"] / data["source_rows"]) if data["source_rows"] else 0
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sales Reporting Automation | Synthetic Demo</title>
<style>
:root{{--bg:#f3f6fa;--ink:#152536;--muted:#64758b;--brand:#137b7d;--border:#dae3eb}}
*{{box-sizing:border-box}}body{{font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;background:var(--bg);color:var(--ink);margin:0}}
main{{max-width:1120px;margin:auto;padding:38px 24px 65px}}.top{{display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap}}
.kicker{{color:var(--brand);font-size:12px;letter-spacing:.14em;font-weight:800}}h1{{font-size:32px;line-height:1.15;margin:10px 0}}h2{{font-size:18px;margin:0 0 19px}}
.small,.sub{{color:var(--muted);font-size:13px}}.tag{{display:inline-block;border:1px solid #b9d9da;background:#edf9f8;color:#126464;border-radius:99px;padding:6px 12px;font-size:12px;font-weight:700}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:29px 0}}.card,.panel{{background:#fff;border:1px solid var(--border);border-radius:12px;box-shadow:0 4px 15px #15253607}}
.card{{padding:19px 18px}}.card span{{display:block;color:var(--muted);font-size:12px}}.card strong{{font-size:25px;letter-spacing:-.03em;display:block;margin-top:8px}}.card small{{font-size:12px;color:var(--muted)}}
.sections{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.panel{{padding:23px;margin-bottom:16px}}.barrow{{display:grid;grid-template-columns:115px 1fr 88px;gap:13px;align-items:center;margin:15px 0}}
.barlabel{{font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.bartrack{{height:12px;background:#e9f0f3;border-radius:7px;overflow:hidden}}.barfill{{display:block;background:var(--brand);height:100%;border-radius:7px}}.barrow b{{font-size:12px;text-align:right}}
table{{width:100%;border-collapse:collapse;font-size:13px}}td,th{{text-align:left;padding:10px 0;border-bottom:1px solid #edf1f4}}th{{color:var(--muted);font-weight:600}}.num{{text-align:right}}.footer{{font-size:12px;color:var(--muted);margin-top:18px}}code{{background:#eef2f6;padding:2px 5px;border-radius:3px}}
@media(max-width:760px){{.grid{{grid-template-columns:repeat(2,1fr)}}.sections{{grid-template-columns:1fr}}main{{padding:22px 15px}}.barrow{{grid-template-columns:92px 1fr 78px;gap:8px}}h1{{font-size:27px}}}}
@media print{{body{{background:white}}main{{max-width:none}}.card,.panel{{box-shadow:none;break-inside:avoid}}}}
/* NEXUS executive reporting system: keeps the generated file self-contained. */
:root {{ --bg:#071829; --ink:#eff5ff; --muted:#aec6df; --brand:#4ea8ff; --border:#294767; }}
body {{
  background: radial-gradient(ellipse at 87% 0%, rgba(78,168,255,.15), transparent 40%),
              radial-gradient(ellipse at 15% 90%, rgba(143,155,255,.07), transparent 42%),
              var(--bg);
}}
main {{ max-width:1260px; padding-top:28px; }}
.top {{
  position:relative; overflow:hidden;
  padding:25px 28px;
  border:1px solid #31577e;
  border-radius:18px;
  background:linear-gradient(115deg,#143958 0%,#0c2944 55%,#0a1b33 100%);
  box-shadow:0 18px 43px rgba(0,8,20,.27);
}}
.top:after {{
  content:"";pointer-events:none;position:absolute;top:-180px;right:-75px;
  width:300px;height:300px;border-radius:50%;
  background:radial-gradient(circle,rgba(78,168,255,.23),transparent 70%);
}}
.kicker {{ color:#95caff; font-size:11px; letter-spacing:.15em; }}
h1 {{ letter-spacing:-.04em; font-size:clamp(27px,3vw,38px); color:#f3f9ff; font-weight:780; }}
h2 {{ font-size:17px; color:#eaf4ff; letter-spacing:-.015em; }}
.sub {{ color:#bdd2e9; }}
.tag {{ background:rgba(7,26,46,.74);border-color:#4a81b5;color:#d6e9fd;border-radius:8px;letter-spacing:.055em; }}
.grid {{ margin:23px 0 25px; gap:13px; }}
.card,.panel {{
  background:linear-gradient(145deg,#133450,#0d263f);
  color:#eaf4ff;
  border:1px solid #31577b;
  border-radius:16px;
  box-shadow:0 14px 30px rgba(1,7,19,.2),inset 0 1px 0 rgba(190,215,250,.065);
}}
.card {{ border-top:2px solid #4ea8ff; min-height:134px; }}
.card:nth-child(2) {{ border-top-color:#8f9bff; }}
.card:nth-child(4) {{ border-top-color:#43c99d; }}
.card span {{ color:#aac3e0; font-weight:650; }}
.card strong {{ color:#f4f9ff; font-size:clamp(23px,2.3vw,30px); font-variant-numeric:tabular-nums; }}
.card small {{ color:#b5cbe5; }}
.sections {{ gap:15px; }}
.panel {{ padding:clamp(17px,2vw,25px); }}
.bartrack {{ background:#0a1f35; height:13px; }}
.barfill {{ background:linear-gradient(90deg,#267bd2,#8f9bff); }}
.barrow b {{ font-variant-numeric:tabular-nums; }}
td,th {{ border-bottom:1px solid #285071; }}
th {{ color:#b7cde5; }}
.footer {{ color:#b1cbe3; }}
code {{ background:#173c5b; color:#c8e3ff; border-radius:5px; }}
@media(max-width:760px) {{ main{{padding:14px 12px 35px}}.top{{padding:20px 16px}}.grid{{gap:9px}} .card{{padding:13px;min-height:115px}} }}
@media(prefers-reduced-motion:reduce) {{ *,*::before,*::after {{ animation-duration:.01ms!important; transition-duration:.01ms!important; }} }}
@media print {{
  body {{ color:#0c2340; background:white!important; }}
  .top,.card,.panel {{ background:#fff!important; color:#0c2340!important; border-color:#a6bbd1!important; box-shadow:none!important; }}
  h1,h2,.card strong,.card span,.barrow b,td,th,.sub,.footer {{ color:#0c2340!important; }}
  .tag {{ color:#0c2340!important; background:#f2f7fc!important; }}
}}
</style></head><body><main>
<div class="top"><div><div class="kicker">NEXUS / SALES DATA INTELLIGENCE · SYNTHETIC CLIENT REPORT</div><h1>From inconsistent files to trusted KPIs</h1><div class="sub">Standalone report generated by Python from <code>sales.csv</code> + <code>customers.xlsx</code>.</div></div><div class="tag">SYNTHETIC DATA ONLY</div></div>
<div class="grid">
<div class="card"><span>Recognized revenue</span><strong>${revenue:,.2f}</strong><small>USD · paid / completed only</small></div>
<div class="card"><span>Valid sales records</span><strong>{data['valid_rows']:,}</strong><small>{quality_rate:.1f}% of source rows</small></div>
<div class="card"><span>Excluded records</span><strong>{data['excluded_rows']:,}</strong><small>Every exclusion is logged</small></div>
<div class="card"><span>Reconciliation</span><strong>{'PASS' if data['reconciliation_passed'] else 'FAIL'}</strong><small>Valid + excluded = {data['source_rows']:,} input rows</small></div>
</div>
<div class="sections"><section class="panel"><h2>Revenue by month</h2>{chart_rows(data['monthly_kpis'],'month')}</section><section class="panel"><h2>Revenue by category</h2>{chart_rows(data['category_kpis'],'category')}</section></div>
<div class="sections"><section class="panel"><h2>Revenue by segment</h2>{chart_rows(data['segment_kpis'],'segment')}</section><section class="panel"><h2>Quality issues</h2><table><thead><tr><th>Issue</th><th class="num">Affected rows</th></tr></thead><tbody>{issue_rows(data['issues'])}</tbody></table><p class="small">A single rejected record may have multiple issues.</p></section></div>
<section class="panel"><h2>Revenue policy & controls</h2><table><tbody>
<tr><td>Paid or completed orders</td><td class="num">{data['paid_or_completed_orders']:,}</td></tr>
<tr><td>Fully refunded orders</td><td class="num">{data['refunded_orders']:,} / ${refunded:,.2f} gross refunded value</td></tr>
<tr><td>Cancelled orders</td><td class="num">{data['cancelled_orders']:,} / ${cancelled:,.2f} cancelled value</td></tr>
<tr><td>Source / accepted / excluded</td><td class="num">{data['source_rows']:,} / {data['valid_rows']:,} / {data['excluded_rows']:,}</td></tr>
</tbody></table><p class="small">Revenue is recognized only for paid or completed orders. Fully refunded and cancelled orders are excluded from recognized revenue and displayed separately, never subtracted twice. This is a demo policy, not an accounting standard.</p></section>
<div class="footer">DEMO · All entities and transactions are fictional. Audit files: <code>cleaned_sales.csv</code>, <code>quality_issues.csv</code>, <code>validation_summary.json</code>. Prepared for independent white-label analytics engagements.</div>
</main></body></html>'''
