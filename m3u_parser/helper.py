import re

# check if the regex is present or not
def is_present(regex, content):
    match = re.search(re.compile(regex, flags=re.IGNORECASE), content)
    return match.group(1) if match else ""


def is_dict(item, ans=None):
    if ans is None:
        ans = []
    tree = []
    for k, v in item.items():
        if isinstance(v, dict):
            ans.append(str(k))
            tree.extend(is_dict(v, ans))
            ans = []
        else:
            if ans:
                ans.append(str(k))
                key = ','.join(ans).replace(',', '_')
                tree.extend([(key, str(v))])
                ans.remove(str(k))
            else:
                tree.extend([(str(k), str(v))])
    return tree


def get_tree(item):
    tree = []
    if isinstance(item, dict):
        tree.extend(is_dict(item, ans=[]))
    elif isinstance(item, list):
        tree = []
        for i in item:
            tree.append(get_tree(i))
    return tree


def render_csv(header, data, out_path='output.csv'):
    input = []
    with open(out_path, 'w') as f:
        dict_writer = csv.DictWriter(f, fieldnames=header)
        dict_writer.writeheader()
        if not isinstance(data[0], list):
            input.append(dict(data))
        else:
            for i in data:
                input.append(dict(i))
        dict_writer.writerows(input)
    return

# convert nested dictionary to csv
def ndict_to_csv(obj, output_path):
    tree = get_tree(obj)
    if isinstance(obj, list):
        header = [i[0] for i in tree[0]]
    else:
        header = [i[0] for i in tree]
    return render_csv(header, tree, output_path)