"""Local preview for the generated static directory."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--port',type=int,default=8741)
parser.add_argument('--base-path',default='',help='Hosting path, e.g. /CPE-Website')
args=parser.parse_args()
base_path='/' + args.base_path.strip('/') if args.base_path.strip('/') else ''
root=Path(__file__).resolve().parents[1]/'dist'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(root),**kw)
    def do_GET(self):
        if base_path:
            if self.path == base_path:
                self.send_response(301)
                self.send_header('Location',base_path+'/')
                self.end_headers()
                return
            if not self.path.startswith(base_path+'/'):
                self.send_error(404)
                return
            self.path=self.path[len(base_path):]
        super().do_GET()
    def log_message(self,*a): pass
server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
print(f'Local: http://127.0.0.1:{args.port}{base_path}/ms/',flush=True)
try: server.serve_forever()
except KeyboardInterrupt: pass
finally: server.server_close()
