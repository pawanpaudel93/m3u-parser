import asyncio
import csv
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
                key = ",".join(ans).replace(",", "_")
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


def render_csv(header, data, out_path="output.csv"):
    input = []
    with open(out_path, "w") as f:
        dict_writer = csv.DictWriter(f, fieldnames=header)
        dict_writer.writeheader()
        if not isinstance(data[0], list):
            input.append(dict(data))
        else:
            for i in data:
                input.append(dict(i))
        dict_writer.writerows(input)


def ndict_to_csv(obj, output_path):
    """Convert nested dictionary to csv.

    :param obj: Stream information list
    :type obj: list
    :param output_path: Path to save the csv file.
    :return: None
    """
    tree = get_tree(obj)
    if isinstance(obj, list):
        header = [i[0] for i in tree[0]]
    else:
        header = [i[0] for i in tree]
    render_csv(header, tree, output_path)


def run_until_completed(coros):
    futures = [asyncio.ensure_future(c) for c in coros]

    async def first_to_finish():
        while True:
            await asyncio.sleep(0)
            for f in futures:
                if f.done():
                    futures.remove(f)
                    return f.result()

    while len(futures) > 0:
        yield first_to_finish()
