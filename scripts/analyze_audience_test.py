"""
Reproducible Audience Preference Test Analysis Script
Growth Engineer Assessment Option 2 - IncuBrix

Calculates:
1. Sample accounting & eligibility verification
2. Format preference shares (Carousel vs Text, Graphic vs Video, Authority)
3. Diagnostic rating means across all 5 dimensions (Clarity, Relevance, Credibility, Usefulness, CTA Intent)
4. Impression of technical rigor / anti-slop distribution
5. Value proposition clarity & trial conversion intent
6. Comparative breakdown between Practitioner Cohort and General Consenting Cohort
"""

import csv
import os
import sys

def run_analysis(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_consenting = len(rows)
    practitioners = [r for r in rows if r['eligibility_verified'] == 'Yes']
    other_consenting = [r for r in rows if r['eligibility_verified'] != 'Yes']

    print("================================================================================")
    print("INCUBRIX AUDIENCE TEST STATISTICAL ANALYSIS REPORT")
    print("================================================================================")
    total_submissions = total_consenting + 1  # 1 non-consenting
    print(f"Total Submissions in Source: {total_submissions}")
    print(f"Excluded Non-Consenting:     1 ({(1/total_submissions)*100:.1f}%)")
    print(f"Total Consenting Cohort:     {total_consenting} ({(total_consenting/total_submissions)*100:.1f}%)")
    print(f"  - Core B2B Practitioners:  {len(practitioners)} ({len(practitioners)/total_consenting*100:.1f}%)")
    print(f"  - Other Consenting:        {len(other_consenting)} ({len(other_consenting)/total_consenting*100:.1f}%)")
    print("================================================================================\n")

    def analyze_subset(name, subset):
        n = len(subset)
        print(f"--- SUBSET: {name} (N = {n}) ---")
        if n == 0:
            print("No data.")
            return

        # Pair 1: Carousel vs Text preference
        p1 = {}
        for r in subset:
            val = r['pair1_preferred_asset']
            p1[val] = p1.get(val, 0) + 1
        print("\n1. Pair 1 Preference (Carousel ast_bp_01 vs Text ast_bp_04):")
        for k, v in sorted(p1.items(), key=lambda x: x[1], reverse=True):
            print(f"   * {k}: {v}/{n} ({v/n*100:.1f}%)")

        # Ratings Pair 1
        dims = ['clarity', 'relevance', 'credibility', 'usefulness', 'cta_intent']
        print("\n   Pair 1 Means (1-5 scale):")
        print(f"   {'Dimension':<15} | {'Carousel':<10} | {'Text':<10} | {'Delta':<10}")
        print("   " + "-" * 50)
        for d in dims:
            c_vals = [float(r[f'pair1_assetA_{d}']) for r in subset if r.get(f'pair1_assetA_{d}')]
            t_vals = [float(r[f'pair1_assetB_{d}']) for r in subset if r.get(f'pair1_assetB_{d}')]
            m_c = sum(c_vals) / len(c_vals) if c_vals else 0
            m_t = sum(t_vals) / len(t_vals) if t_vals else 0
            print(f"   {d.capitalize():<15} | {m_c:<10.2f} | {m_t:<10.2f} | {m_c - m_t:+10.2f}")

        # Pair 2: Graphic vs Video preference
        p2 = {}
        for r in subset:
            val = r['pair2_preferred_asset']
            p2[val] = p2.get(val, 0) + 1
        print("\n2. Pair 2 Preference (Graphic ast_bp_05 vs Video ast_bp_03):")
        for k, v in sorted(p2.items(), key=lambda x: x[1], reverse=True):
            print(f"   * {k}: {v}/{n} ({v/n*100:.1f}%)")

        # Ratings Pair 2
        print("\n   Pair 2 Means (1-5 scale):")
        print(f"   {'Dimension':<15} | {'Graphic':<10} | {'Video':<10} | {'Delta':<10}")
        print("   " + "-" * 50)
        for d in dims:
            g_vals = [float(r[f'pair2_assetA_{d}']) for r in subset if r.get(f'pair2_assetA_{d}')]
            v_vals = [float(r[f'pair2_assetB_{d}']) for r in subset if r.get(f'pair2_assetB_{d}')]
            m_g = sum(g_vals) / len(g_vals) if g_vals else 0
            m_v = sum(v_vals) / len(v_vals) if v_vals else 0
            print(f"   {d.capitalize():<15} | {m_g:<10.2f} | {m_v:<10.2f} | {m_g - m_v:+10.2f}")

        # Pair 3: Authority
        p3 = {}
        for r in subset:
            val = r['pair3_preferred_asset']
            p3[val] = p3.get(val, 0) + 1
        print("\n3. Pair 3 Technical Authority (Carousel ast_bp_19 vs Post ast_bp_26):")
        for k, v in sorted(p3.items(), key=lambda x: x[1], reverse=True):
            print(f"   * {k}: {v}/{n} ({v/n*100:.1f}%)")

        # Anti-slop
        slop = {}
        for r in subset:
            val = r['pair3_anti_slop_rating']
            slop[val] = slop.get(val, 0) + 1
        print("\n4. Technical Rigor / Anti-Slop Impression:")
        for k, v in sorted(slop.items(), key=lambda x: x[1], reverse=True):
            print(f"   * {k}: {v}/{n} ({v/n*100:.1f}%)")

        # Value prop clarity
        vp = {}
        for r in subset:
            val = r['value_prop_clarity']
            vp[val] = vp.get(val, 0) + 1
        print("\n5. Value Proposition Clarity:")
        for k, v in sorted(vp.items(), key=lambda x: x[1], reverse=True):
            print(f"   * {k}: {v}/{n} ({v/n*100:.1f}%)")

        # Trial intent
        ti = {}
        for r in subset:
            val = r['trial_conversion_intent']
            ti[val] = ti.get(val, 0) + 1
        print("\n6. Trial Conversion Likelihood:")
        for k, v in sorted(ti.items(), key=lambda x: x[1], reverse=True):
            print(f"   * {k}: {v}/{n} ({v/n*100:.1f}%)")
        print("\n" + "=" * 80 + "\n")

    analyze_subset("FULL CONSENTING COHORT", rows)
    analyze_subset("CORE B2B PRACTITIONER COHORT", practitioners)
    analyze_subset("OTHER CONSENTING RESPONDENTS", other_consenting)

if __name__ == '__main__':
    csv_file = os.path.join(r"D:\Projects\Incubrix-Growth\research", "audience_test_responses.csv")
    run_analysis(csv_file)
