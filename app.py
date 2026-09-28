"""Run: python app.py  |  Python 3.10+; standard library only."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, sqlite3, argparse
from seed import initialize, dataset, ROOT
from model import project
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'dist'),**kwargs)
    def send_json(self,data,status=200):
        body=json.dumps(data).encode(); self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path=='/api/data':return self.send_json(dataset())
        if self.path=='/api/scenarios':
            with sqlite3.connect(ROOT/'wallet.db') as c:
                c.row_factory=sqlite3.Row
                return self.send_json([dict(r) for r in c.execute('SELECT * FROM scenarios ORDER BY id DESC')])
        # Serve public assets only; never expose Python source or database.
        return super().do_GET()
    def do_POST(self):
        if self.path not in ['/api/project','/api/scenarios']:return self.send_json({'error':'Not found'},404)
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send_json({'error':'JSON required'},415)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=10000:raise ValueError('Invalid request size')
            body=json.loads(self.rfile.read(length));period=body['period'];a=body['assumptions']
            v=next(p['values'] for p in dataset()['periods'] if p['id']==period)
            result=project(v,a)
            if self.path=='/api/project':return self.send_json(result)
            name=str(body.get('name','Scenario')).strip()[:100]
            if not name:raise ValueError('Name required')
            with sqlite3.connect(ROOT/'wallet.db') as c:
                cur=c.execute('INSERT INTO scenarios(name,period_id,assumptions) VALUES(?,?,?)',(name,period,json.dumps(a)))
            return self.send_json({'id':cur.lastrowid,'name':name},201)
        except (ValueError,KeyError,TypeError,StopIteration):return self.send_json({'error':'Invalid period, assumptions or request.'},400)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8000);args=p.parse_args()
    initialize(); print(f'Company Wallet: http://localhost:{args.port}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
