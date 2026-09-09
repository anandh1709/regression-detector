def category_pass_rate(results):
    correct = 0
    for i in results:
        if i["expected_category"] == i["actual_category"]:
            correct += 1
    pass_rate = (correct/len(results)) * 100
    return round(pass_rate, 2)
