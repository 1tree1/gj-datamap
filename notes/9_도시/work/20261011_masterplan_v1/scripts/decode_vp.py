"""라이노 get_viewport_image 결과(tool-results 텍스트)에서 JPG를 꺼낸다. 사용: decode_vp.py <txt> <out.jpg>"""
import json, base64, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
img = [c for c in d['content'] if c.get('mimeType') == 'image/jpeg' or c.get('type') == 'image'][0]
open(sys.argv[2], 'wb').write(base64.b64decode(img.get('data') or img.get('text')))
meta = [c['text'] for c in d['content'] if c.get('type') == 'text' and 'metadata' in c.get('text', '')]
print(sys.argv[2], (meta[0][:300] if meta else ''))
