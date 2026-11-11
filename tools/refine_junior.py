import json
from pathlib import Path
from junior_filter import junior_words


def read(name):
    text = Path('data', name + '.js').read_text(encoding='utf-8')
    return [line.split('\t') for line in json.loads(text[text.index(',') + 1:-3]).split('\n')]

items = junior_words(read('junior'), read('primary'))
body = '\n'.join('\t'.join(row) for row in items)
Path('data/junior.js').write_text('KB_DATA("junior",' + json.dumps(body, ensure_ascii=False) + ');\n', encoding='utf-8')
print(len(items))
