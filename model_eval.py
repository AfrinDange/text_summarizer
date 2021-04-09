from rouge_score import rouge_scorer
import json
import sys
human_summary = sys.argv[1]
computer_summary = sys.argv[2]
print(human_summary)
print(computer_summary)
scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL', 'rougeLsum'], use_stemmer=True)
scores = scorer.score(human_summary, computer_summary)

for key, val in scores.items():
    scores[key] = str(val)
print(json.dumps(scores))