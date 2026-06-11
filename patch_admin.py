from pathlib import Path
import re
p = Path('admin.html')
text = p.read_text(encoding='utf-8')
text, n1 = re.subn(r'"price":"₹\s*([0-9,]+)\s*[–-]\s*₹\s*[0-9,]+"', lambda m: f'"price":"₹{m.group(1)}"', text)
text, n2 = re.subn(r'\s*"price_min"\s*:\s*[0-9]+,?', '', text)
text, n3 = re.subn(r'\s*"price_max"\s*:\s*[0-9]+,?', '', text)
text = re.sub(r',\s*([}\]])', r'\1', text)
text = text.replace(".split('–')[0]", '')
p.write_text(text, encoding='utf-8')
print('ranges replaced:', n1)
print('price_min removed:', n2)
print('price_max removed:', n3)
