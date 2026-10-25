import csv
import os

bp_path = r'research/asset_blueprint.csv'
with open(bp_path, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows in blueprint: {len(rows)}")
print(f"{'ID':<20} | {'Platform':<15} | {'Format':<12} | {'Source Exists':<30} | {'Final Exists':<30}")
print("-" * 115)

src_dir = os.path.join('outputs', 'source')
fin_dir = os.path.join('outputs', 'final')

stats = {
    'total': len(rows),
    'formats': {},
    'platforms': {},
    'source_present': 0,
    'final_present': 0,
    'by_format': {
        'short_video': {'total': 0, 'source': 0, 'final': 0},
        'carousel': {'total': 0, 'source': 0, 'final': 0},
        'graphic': {'total': 0, 'source': 0, 'final': 0},
        'text_post': {'total': 0, 'source': 0, 'final': 0},
    }
}

for r in rows:
    a_id = r['asset_id']
    fmt = r['format']
    plat = r['platform']
    
    stats['formats'][fmt] = stats['formats'].get(fmt, 0) + 1
    stats['platforms'][plat] = stats['platforms'].get(plat, 0) + 1
    stats['by_format'][fmt]['total'] += 1

    src_found = []
    fin_found = []

    for sub in ['videos', 'carousels', 'graphics', 'copy']:
        s_path = os.path.join(src_dir, sub)
        f_path = os.path.join(fin_dir, sub)
        if os.path.exists(s_path):
            for file in os.listdir(s_path):
                if file.startswith(a_id):
                    src_found.append(file)
        if os.path.exists(f_path):
            for file in os.listdir(f_path):
                if file.startswith(a_id):
                    fin_found.append(file)

    if src_found:
        stats['source_present'] += 1
        stats['by_format'][fmt]['source'] += 1
    if fin_found:
        stats['final_present'] += 1
        stats['by_format'][fmt]['final'] += 1

    src_str = ', '.join(src_found) if src_found else 'MISSING'
    fin_str = ', '.join(fin_found) if fin_found else 'MISSING'
    print(f"{a_id:<20} | {plat:<15} | {fmt:<12} | {src_str:<30} | {fin_str:<30}")

print("\n" + "=" * 50)
print("AUDIT SUMMARY:")
print(f"Total blueprint assets: {stats['total']}")
print(f"Formats: {stats['formats']}")
print(f"Platforms: {stats['platforms']}")
print(f"Source present: {stats['source_present']}/{stats['total']}")
print(f"Final present: {stats['final_present']}/{stats['total']}")
print("Breakdown by format:")
for fmt, cnts in stats['by_format'].items():
    print(f"  {fmt:<12}: Total={cnts['total']}, Source={cnts['source']}, Final={cnts['final']}")
