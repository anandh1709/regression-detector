def category_pass_rate(results):
    correct = 0
    for i in results:
        if i["expected_category"] == i["actual_category"]:
            correct += 1
    pass_rate = (correct/len(results)) * 100
    return round(pass_rate, 2)

def average_latency(results):
    total_latency = 0
    for i in results:
        total_latency += i["latency"]
    avg_latency = total_latency/len(results)
    return round(avg_latency, 2) 

def average_completion_tokens(results):
    total_tokens = 0
    for i in results:
        total_tokens += i["completion_tokens"]
    avg_tokens = total_tokens/len(results)
    return round(avg_tokens, 2)
        