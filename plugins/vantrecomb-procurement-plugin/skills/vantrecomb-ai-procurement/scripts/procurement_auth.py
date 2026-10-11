"""Standard-library OAuth device login with private, expiring local sessions."""
import base64
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
import webbrowser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

SCOPES = {
    'ai:rfq:read': '/api/v1/ai/me/rfqs',
    'me:profile:read': '/api/v1/ai/me/profile',
    'me:profile:write': None,
    'me:quotes:read': '/api/v1/ai/me/quotes',
    'me:quotes:respond': None,
    'me:files:download': '/api/v1/ai/me/files',
    'me:orders:read': '/api/v1/ai/me/orders',
    'me:shipments:read': '/api/v1/ai/me/shipments',
}

def redact(value):
    if isinstance(value, dict):
        return {k: '[redacted]' if k.lower() in {'token','access_token','refresh_token','account_token','rfq_token','device_code','code_verifier','authorization'} else redact(v) for k,v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return re.sub(r'\b(?:apt|rft|odc)_[A-Za-z0-9_-]+','[redacted]',value)
    return value

class SameOriginRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        def origin(url):
            u=urlsplit(url)
            return u.scheme,u.hostname,u.port or (443 if u.scheme=='https' else 80)
        if origin(req.full_url)!=origin(newurl):
            raise ValueError('refusing a redirect to another origin')
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def urlopen(request, timeout=30):
    return build_opener(SameOriginRedirectHandler()).open(request, timeout=timeout)

def load_config():
    # Configuration follows the skill location; process environment always wins.
    path=Path(__file__).resolve().parent.parent / '.env'
    if not path.exists(): return
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        match=re.match(r'\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)',line)
        if not match: continue
        key,value=match.groups()
        if key not in {'VANTRECOMB_API_ORIGIN','VANTRECOMB_OAUTH_CLIENT_ID'}: continue
        value=value.strip()
        if value.startswith(('"',"'")):
            end=value.find(value[0],1)
            if end<0: raise ValueError('invalid quoted local configuration')
            value=value[1:end]
        else: value=re.split(r'\s+#',value,maxsplit=1)[0].strip()
        os.environ.setdefault(key,value)

def _session_path(origin):
    base=os.getenv('VANTRECOMB_AUTH_DIR')
    if not base:
        base=str(Path(os.getenv('LOCALAPPDATA',str(Path.home()))) / 'VantrecombProcurement') if os.name=='nt' else str(Path.home()/'.local/share/vantrecomb-procurement')
    return Path(base)/(hashlib.sha256(origin.encode()).hexdigest()+'.session')

def _dpapi(data, decrypt=False):
    class Blob(ctypes.Structure):
        _fields_=[('size',ctypes.c_ulong),('data',ctypes.POINTER(ctypes.c_ubyte))]
    buffer=(ctypes.c_ubyte*len(data)).from_buffer_copy(data)
    source=Blob(len(data),buffer); target=Blob()
    crypt=ctypes.WinDLL('crypt32',use_last_error=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    function=crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    function.argtypes=[ctypes.POINTER(Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong,ctypes.POINTER(Blob)]
    function.restype=ctypes.c_int
    kernel.LocalFree.argtypes=[ctypes.c_void_p];kernel.LocalFree.restype=ctypes.c_void_p
    if not function(ctypes.byref(source),None,None,None,None,1,ctypes.byref(target)):
        raise OSError('Windows credential protection failed')
    try: return ctypes.string_at(target.data,target.size)
    finally: kernel.LocalFree(target.data)

def save_session(origin,response):
    duration=int(response.get('expires_in',0))
    if not response.get('access_token') or not 0<duration<=1800:
        raise ValueError('refusing to cache a missing or long-lived OAuth token')
    value={'access_token':response['access_token'],'scope':response.get('scope',''),'expires_at':time.time()+duration,'origin':origin}
    raw=json.dumps(value).encode()
    envelope={'format':'dpapi' if os.name=='nt' else 'private-session','data':base64.b64encode(_dpapi(raw) if os.name=='nt' else raw).decode()}
    target=_session_path(origin);target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    descriptor,temporary=tempfile.mkstemp(dir=target.parent,prefix='.session-')
    try:
        with os.fdopen(descriptor,'w',encoding='utf-8') as handle:
            json.dump(envelope,handle)
        if os.name!='nt':os.chmod(temporary,0o600)
        os.replace(temporary,target)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)

def clear_session(origin):
    _session_path(origin).unlink(missing_ok=True)

def read_session(origin):
    target=_session_path(origin)
    if not target.exists():return {}
    if os.name!='nt' and target.stat().st_mode&0o077:
        raise ValueError('session file is accessible to other users; fix permissions or log in again')
    envelope=json.loads(target.read_text(encoding='utf-8'))
    raw=base64.b64decode(envelope['data'])
    if envelope['format']=='dpapi':
        if os.name!='nt':raise ValueError('Windows sessions cannot be copied to another machine; log in again')
        raw=_dpapi(raw,decrypt=True)
    elif os.name=='nt':raise ValueError('refusing an unprotected Windows session')
    value=json.loads(raw)
    if value.get('origin')!=origin or value.get('expires_at',0)<=time.time():
        clear_session(origin);return {}
    return value

class OAuthError(RuntimeError):
    def __init__(self,code,status):
        self.code=code
        super().__init__(f'OAuth HTTP {status}: {code}')

def oauth_form(origin,path,data,timeout=30):
    if path not in {'/oauth/device/code','/oauth/token'}:raise ValueError('unsupported OAuth endpoint')
    req=Request(origin+path,data=urlencode(data).encode(),headers={'Content-Type':'application/x-www-form-urlencoded'},method='POST')
    try:
        with urlopen(req,timeout=timeout) as response:return json.loads(response.read())
    except HTTPError as error:
        try:details=json.loads(error.read())
        except (ValueError,OSError):details={}
        raise OAuthError(details.get('error') or details.get('code') or 'authorization_failed',error.code) from None
    except URLError:raise RuntimeError('OAuth service unavailable') from None

def auth_device(args):
    requested=(args.scope or '').split()
    if not requested or any(scope not in SCOPES for scope in requested):
        raise ValueError('specify valid minimal --scope values; use scopes to list them')
    clear_session(args.origin)
    response=oauth_form(args.origin,'/oauth/device/code',{'client_id':args.client_id,'scope':' '.join(requested)},args.timeout)
    verification=response['verification_uri_complete']
    parsed=urlsplit(verification)
    if parsed.scheme!='https' or parsed.username or parsed.password:raise ValueError('unsafe verification URL')
    print('Authorize at: '+verification)
    print('Code: '+response['user_code'])
    if not args.no_browser:webbrowser.open(verification)
    interval=max(1,int(response.get('interval',5)))
    deadline=time.monotonic()+min(600,int(response.get('expires_in',600)))
    while time.monotonic()<deadline:
        time.sleep(interval)
        if time.monotonic()>=deadline:break
        try:
            token=oauth_form(args.origin,'/oauth/token',{'grant_type':'urn:ietf:params:oauth:grant-type:device_code','client_id':args.client_id,'device_code':response['device_code']},args.timeout)
        except OAuthError as error:
            if error.code=='authorization_pending':continue
            if error.code=='slow_down':interval+=5;continue
            raise
        save_session(args.origin,token)
        print('Account connected. Scope: '+token.get('scope','')+'. Session expires in '+str(token.get('expires_in',0))+' seconds.')
        return 0
    raise RuntimeError('authorization expired; start a new login')
