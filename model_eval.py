from rouge_score import rouge_scorer
import json
import sys
human_summary = sys.argv[1]
computer_summary = sys.argv[2]
output = {}
output['humanSumm'] = human_summary
output['compSumm'] = computer_summary
scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL', 'rougeLsum'], use_stemmer=True)
scores = scorer.score(human_summary, computer_summary)
metrics = {}
for key, val in scores.items():
    values = []
    for i in range(len(scores[key])):
        values.append(round(scores[key][i], 3))
    metrics[key] = values
output['scores'] = metrics
print(json.dumps(output))