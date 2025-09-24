#!/usr/bin/env python3
"""
Generate comprehensive improvement report from iterative test results
"""
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

def generate_improvement_report(history_file: str):
    """Generate comprehensive report from improvement history"""
    
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    report_dir = Path(history_file).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    
    iterations = history["iterations"]
    iteration_numbers = [i["iteration"] for i in iterations]
    overall_scores = [i["scoring_results"]["evaluation_summary"]["overall_score"] for i in iterations]
    
    plt.figure(figsize=(12, 8))
    plt.plot(iteration_numbers, overall_scores, 'b-o', linewidth=2, markersize=8)
    plt.axhline(y=history["target_score"], color='r', linestyle='--', label=f'Target Score ({history["target_score"]})')
    plt.xlabel('Iteration')
    plt.ylabel('Overall Score')
    plt.title('Trip Guide Quality Score Progression')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.ylim(0, 100)
    
    chart_path = report_dir / "score_progression.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    report_content = f"""

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Destination:** {history['trip_data']['destination']}
**Target Score:** {history['target_score']}/100


- **Final Score:** {history['final_result']['final_score']}/100
- **Iterations Completed:** {len(iterations)}
- **Target Achieved:** {'✅ YES' if history['final_result']['success'] else '❌ NO'}
- **Score Improvement:** +{overall_scores[-1] - overall_scores[0]:.1f} points


![Score Progression]({chart_path.name})


"""
    
    for iteration in iterations:
        scores = iteration["scoring_results"]["detailed_scores"]
        summary = iteration["scoring_results"]["evaluation_summary"]
        
        report_content += f"""

**Overall Score:** {summary['overall_score']}/100 (Grade: {summary['grade']})

**Category Breakdown:**
- Validation: {scores['validation']['score']}/100
- PRD Compliance: {scores['prd_compliance']['score']}/100  
- Luxury Standards: {scores['luxury_standards']['score']}/100
- User Experience: {scores['user_experience']['score']}/100

**Key Issues:**
"""
        
        if scores['validation']['errors']:
            report_content += f"- **Validation:** {scores['validation']['errors'][0]}\n"
        if scores['prd_compliance']['suggestions']:
            report_content += f"- **PRD:** {scores['prd_compliance']['suggestions'][0]}\n"
        if scores['luxury_standards']['critiques']:
            luxury_critiques = [c for c in scores['luxury_standards']['critiques'] if '❌' in c]
            if luxury_critiques:
                report_content += f"- **Luxury:** {luxury_critiques[0]}\n"
        
        if iteration.get('improvements_applied'):
            report_content += f"\n**Improvements Applied for Next Iteration:**\n"
            for imp in iteration['improvements_applied'][:3]:
                report_content += f"- {imp}\n"
    
    report_file = report_dir / "improvement_report.md"
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    print(f"📊 Improvement report generated: {report_file}")
    return report_file

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        history_file = sys.argv[1]
    else:
        history_files = list(Path("output").glob("**/complete_improvement_history.json"))
        if history_files:
            history_file = str(sorted(history_files)[-1])
        else:
            print("No improvement history files found")
            sys.exit(1)
    
    generate_improvement_report(history_file)
