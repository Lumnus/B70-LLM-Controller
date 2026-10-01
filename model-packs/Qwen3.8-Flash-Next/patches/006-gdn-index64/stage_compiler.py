import concurrent.futures, hashlib, json, pathlib, subprocess, urllib.request
root=pathlib.Path('build/gdn-index64/toolchain').resolve()
lock=json.load(open('build/gdn-index64/compiler-lock.json'))
(root/'debs').mkdir(parents=True,exist_ok=True)
json.dump(lock,open(root/'source-lock.json','w'),indent=2)
def fetch(item):
 name,sha=item; dst=root/'debs'/name
 if not dst.exists() or hashlib.sha256(dst.read_bytes()).hexdigest()!=sha:
  urllib.request.urlretrieve(lock['pool_base']+name,dst)
 assert hashlib.sha256(dst.read_bytes()).hexdigest()==sha,name
 print('verified',name,flush=True)
 return dst
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 paths=list(ex.map(fetch,lock['debs'].items()))
for p in paths:
 subprocess.run(['dpkg-deb','-x',str(p),str(root/'oneapi')],check=True)
print('COMPILER_STAGED',flush=True)
