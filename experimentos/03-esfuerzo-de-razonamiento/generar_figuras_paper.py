#!/usr/bin/env python3
"""Generate publication figures (EN and ES) directly from Experiment 03 CSV data."""
import csv
from pathlib import Path
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
RES = ROOT / 'resultados'
OUT_DIR = ROOT / 'paper' / 'figuras'
LEVELS = ['low', 'medium', 'high', 'xhigh', 'max']
MODELS = [
    ('gpt-6.1-sol', 'gpt-6.1-sol (Codex)'),
    ('gpt-6-luna', 'gpt-6-luna (Codex)'),
    ('claude-haiku-5-5', 'claude-haiku-5-5'),
    ('claude-opus-5-5', 'claude-opus-5-5'),
    ('claude-fable-5-2', 'claude-fable-5-2'),
]

COLORS = {
    'gpt-6.1-sol': '#1b4965',
    'gpt-6-luna': '#2a9d8f',
    'claude-haiku-5-5': '#e9c46a',
    'claude-opus-5-5': '#f4a261',
    'claude-fable-5-2': '#c1121f',
}


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def load_matrix():
    sol = read_csv(RES / 'crudo.csv') + [
        r for r in read_csv(RES / 'crudo-extension.csv') if r['nivel'] in ('xhigh', 'max')
    ]
    luna = read_csv(RES / 'crudo-gpt-6-luna.csv')
    haiku = read_csv(RES / 'crudo-claude-haiku-5-5-02-02.csv')
    opus = read_csv(RES / 'crudo-claude-opus-5-5-02-02.csv')
    fable_02 = [r for r in read_csv(RES / 'crudo-fable-02-02.csv') if r.get('cuota') != '1']
    fable_03 = read_csv(RES / 'crudo-fable-02-03.csv')
    return {
        'gpt-6.1-sol': sol,
        'gpt-6-luna': luna,
        'claude-haiku-5-5': haiku,
        'claude-opus-5-5': opus,
        'claude-fable-5-2': fable_02 + fable_03,
    }


def setup_style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 10,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'grid.alpha': 0.25,
        'grid.linestyle': '--',
        'figure.facecolor': '#ffffff',
        'axes.facecolor': '#ffffff',
    })


def save_both(fig, stem):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f'{stem}.png', dpi=220, bbox_inches='tight')
    fig.savefig(OUT_DIR / f'{stem}.svg', bbox_inches='tight')
    plt.close(fig)


def plot_fig1_resolution(data, lang):
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    matrix = np.zeros((len(MODELS), len(LEVELS)), dtype=float)
    labels = []
    for i, (key, label) in enumerate(MODELS):
        labels.append(label)
        rows = data[key]
        for j, lvl in enumerate(LEVELS):
            sub = [r for r in rows if r['nivel'] == lvl]
            solved = sum(int(r['resuelta']) for r in sub)
            matrix[i, j] = 100.0 * solved / len(sub)

    im = ax.imshow(matrix, cmap='RdYlGn', vmin=0, vmax=100, aspect='auto')
    ax.set_xticks(range(len(LEVELS)))
    ax.set_xticklabels(LEVELS, fontweight='bold')
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels(labels)

    for i, (key, _) in enumerate(MODELS):
        rows = data[key]
        for j, lvl in enumerate(LEVELS):
            sub = [r for r in rows if r['nivel'] == lvl]
            solved = sum(int(r['resuelta']) for r in sub)
            pct = 100.0 * solved / len(sub)
            color = '#ffffff' if pct < 45 else '#111827'
            ax.text(j, i, f'{solved}/{len(sub)}\n({pct:.0f}%)', ha='center', va='center',
                    color=color, fontsize=9.5, fontweight='bold' if solved < 24 else 'normal')

    ax.grid(False)
    title = (
        'Task Resolution Within 600s Deadline Across Reasoning Levels (n = 24 / cell)'
        if lang == 'en' else
        'Resolución dentro del plazo de 600 s por modelo y nivel (n = 24 por celda)'
    )
    ax.set_title(title, fontsize=11.5, fontweight='bold', pad=12)
    cbar = fig.colorbar(im, ax=ax, fraction=0.032, pad=0.03)
    cbar.set_label('% Solved' if lang == 'en' else '% Resueltas')
    save_both(fig, f'fig1-resolution-{lang}')


def plot_fig2_latency(data, lang):
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    x = np.arange(len(LEVELS))
    for key, label in MODELS:
        rows = data[key]
        meds = [
            statistics.median([float(r['segundos']) for r in rows if r['nivel'] == lvl and r['segundos']])
            for lvl in LEVELS
        ]
        ratio = meds[-1] / meds[0]
        ax.plot(x, meds, marker='o', linewidth=2.4, markersize=7, color=COLORS[key],
                label=f'{label}  ({ratio:.2f}x)')
        for xi, yi in zip(x, meds):
            if (key == 'claude-fable-5-2' and xi in (3, 4)) or (key == 'claude-opus-5-5' and xi == 4) or (key == 'claude-haiku-5-5' and xi == 4):
                offset = (0, 8) if yi < 580 else (-16, -15)
                ax.annotate(f'{yi:.0f}s', (xi, yi), textcoords='offset points', xytext=offset,
                            fontsize=8.5, fontweight='bold', color=COLORS[key], ha='center')

    ax.axhline(600, color='#6b7280', linestyle='--', linewidth=1.4)
    limit_lbl = '600 s timeout ceiling' if lang == 'en' else 'Límite estricto de 600 s (timeout)'
    ax.text(2.25, 614, limit_lbl, color='#4b5563', fontsize=8.8, fontweight='bold', ha='center')

    ax.set_xticks(x)
    ax.set_xticklabels(LEVELS, fontweight='bold')
    ax.set_ylim(0, 665)
    ax.set_ylabel('Median wall-clock time (s)' if lang == 'en' else 'Mediana de tiempo de reloj (s)')
    ax.set_xlabel('Configured reasoning effort' if lang == 'en' else 'Nivel de esfuerzo configurado')
    title = (
        'Median Wall-Clock Latency by Reasoning Effort (with max/low ratio)'
        if lang == 'en' else
        'Mediana de tiempo por nivel de esfuerzo (con razón max/low)'
    )
    ax.set_title(title, fontsize=11.5, fontweight='bold', pad=12)
    ax.legend(loc='upper left', frameon=True, facecolor='#ffffff', framealpha=0.92, fontsize=9)
    save_both(fig, f'fig2-latency-{lang}')


def plot_fig3_failures(data, lang):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.3), gridspec_kw={'width_ratios': [1.25, 1.0]})

    # Panel A: Timeout / Failure breakdown at max for Claude models
    max_models = ['claude-haiku-5-5', 'claude-opus-5-5', 'claude-fable-5-2']
    short_names = ['Haiku 5.5\n(max)', 'Opus 5.5\n(max)', 'Fable 5.2\n(max)']
    solved_in_time, timeout_pass_disk, timeout_fail_disk = [], [], []
    for key in max_models:
        sub = [r for r in data[key] if r['nivel'] == 'max']
        solved = sum(int(r['resuelta']) for r in sub)
        to_pass = sum(1 for r in sub if r['timeout'] == '1' and r['tests_aprobados'] == r['tests_total'])
        to_fail = sum(1 for r in sub if r['timeout'] == '1' and r['tests_aprobados'] != r['tests_total'])
        solved_in_time.append(solved)
        timeout_pass_disk.append(to_pass)
        timeout_fail_disk.append(to_fail)

    x1 = np.arange(len(max_models))
    l1 = 'Solved <= 600s' if lang == 'en' else 'Resuelta <= 600 s'
    l2 = 'Timeout (600s), tests pass on disk' if lang == 'en' else 'Timeout (600 s), tests pasan en disco'
    l3 = 'Timeout (600s), 0 lines edited' if lang == 'en' else 'Timeout (600 s), 0 líneas editadas'

    p1 = ax1.bar(x1, solved_in_time, width=0.52, color='#2a9d8f', label=l1)
    p2 = ax1.bar(x1, timeout_pass_disk, width=0.52, bottom=solved_in_time, color='#f4a261', label=l2)
    bottom2 = np.array(solved_in_time) + np.array(timeout_pass_disk)
    p3 = ax1.bar(x1, timeout_fail_disk, width=0.52, bottom=bottom2, color='#c1121f', label=l3)

    for idx in range(len(x1)):
        for vals, base in [(solved_in_time, np.zeros(3)), (timeout_pass_disk, np.array(solved_in_time)), (timeout_fail_disk, bottom2)]:
            v = vals[idx]
            if v > 0:
                ax1.text(idx, base[idx] + v / 2, str(v), ha='center', va='center',
                         color='#ffffff' if v != timeout_pass_disk[idx] else '#111827',
                         fontweight='bold', fontsize=9.5)

    ax1.set_xticks(x1)
    ax1.set_xticklabels(short_names, fontweight='bold')
    ax1.set_ylim(0, 32.5)
    ax1.set_ylabel('Runs (out of 24)' if lang == 'en' else 'Corridas (sobre 24)')
    ax1.set_title(
        'A. Outcome Anatomy at max Effort (Claude)' if lang == 'en' else 'A. Anatomía de resultados en max (Claude)',
        fontsize=10.5, fontweight='bold'
    )
    ax1.legend(loc='upper right', fontsize=8.2, frameon=True)

    # Panel B: Token scaling (median tokens relative to low=1.0x across levels where n>=21)
    x2 = np.arange(len(LEVELS))
    for key, label in MODELS:
        rows = data[key]
        med_tokens = []
        valid_x = []
        base_tok = statistics.median([int(r['tokens_totales']) for r in rows if r['nivel'] == 'low' and r['tokens_totales']])
        for j, lvl in enumerate(LEVELS):
            toks = [int(r['tokens_totales']) for r in rows if r['nivel'] == lvl and r['tokens_totales']]
            # Only plot connected curve where receipt completeness >= 20/24; annotate Fable max separately
            if len(toks) >= 20:
                valid_x.append(j)
                med_tokens.append(statistics.median(toks) / base_tok)
        ax2.plot(valid_x, med_tokens, marker='s', linewidth=2.1, markersize=6, color=COLORS[key], label=label.split(' ')[0])

    # Mark Fable max partial n=4 receipt point as hollow marker
    fable_rows = data['claude-fable-5-2']
    f_low = statistics.median([int(r['tokens_totales']) for r in fable_rows if r['nivel'] == 'low' and r['tokens_totales']])
    f_max_toks = [int(r['tokens_totales']) for r in fable_rows if r['nivel'] == 'max' and r['tokens_totales']]
    f_max_ratio = statistics.median(f_max_toks) / f_low
    ax2.plot([4], [f_max_ratio], marker='s', markersize=7, markerfacecolor='#ffffff',
             markeredgecolor=COLORS['claude-fable-5-2'], markeredgewidth=2.0)
    lbl_n4 = 'Fable max\n(n=4 only)' if lang == 'en' else 'Fable max\n(sólo n=4)'
    ax2.annotate(lbl_n4, (4, f_max_ratio), textcoords='offset points', xytext=(-18, -28),
                 ha='center', fontsize=8, color=COLORS['claude-fable-5-2'], fontweight='bold')

    ax2.set_xticks(x2)
    ax2.set_xticklabels(LEVELS, fontweight='bold')
    ax2.set_ylim(0.5, 8.0)
    ax2.set_ylabel('Median tokens relative to low (1.0x)' if lang == 'en' else 'Tokens medianos relativos a low (1,0×)')
    ax2.set_title(
        'B. Within-CLI Token Scaling (low = 1.0x)' if lang == 'en' else 'B. Escalamiento de tokens intra-CLI (low = 1,0×)',
        fontsize=10.5, fontweight='bold'
    )
    ax2.legend(loc='upper left', fontsize=8.2, frameon=True)

    save_both(fig, f'fig3-anatomy-tokens-{lang}')


def main():
    setup_style()
    data = load_matrix()
    for lang in ('en', 'es'):
        plot_fig1_resolution(data, lang)
        plot_fig2_latency(data, lang)
        plot_fig3_failures(data, lang)
    print('Generated 6 figures (PNG + SVG) in', OUT_DIR)


if __name__ == '__main__':
    main()
