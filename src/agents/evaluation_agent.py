def normalize_value(v):
    try:
        return round(float(v), 2)
    except:
        return v


def field_accuracy(pred_rows, gt_rows):
    total, correct = 0, 0

    for p, g in zip(pred_rows, gt_rows):
        for field in g:
            total += 1
            if normalize_value(p.get(field)) == normalize_value(g.get(field)):
                correct += 1

    return (correct / total) * 100 if total else 0.0


def numeric_accuracy(pred_rows, gt_rows, tolerance=0.05):
    total, correct = 0, 0

    for p, g in zip(pred_rows, gt_rows):
        for field in ["open", "high", "low", "close", "volume"]:
            total += 1
            try:
                if abs(float(p[field]) - float(g[field])) <= tolerance * float(g[field]):
                    correct += 1
            except:
                pass

    return (correct / total) * 100 if total else 0.0


def row_accuracy(pred_rows, gt_rows):
    matched = 0
    for p, g in zip(pred_rows, gt_rows):
        if all(
            normalize_value(p[k]) == normalize_value(g[k])
            for k in g
        ):
            matched += 1

    return (matched / len(gt_rows)) * 100 if gt_rows else 0.0
