from flask import Flask, request, jsonify, render_template_string, session, redirect
import requests
import re
import json
from urllib.parse import urlparse, urljoin
import urllib3
urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = 'bronx_reverse_engineer_v4_2024'

ADMIN_USER = "bronx"
ADMIN_PASS = "ultra2026"

# ============================================
# 💀 ULTIMATE API REVERSE ENGINEER v4.0
# ============================================
def reverse_engineer_api(target_url, test_param="9876543210"):
    all_logs = []
    results = {
        'original_url': target_url,
        'real_api': None,
        'all_apis_found': [],
        'tested_apis': [],
        'error_logs': [],
        'success_logs': []
    }
    
    def log(msg, level="INFO"):
        entry = f"[{level}] {msg}"
        all_logs.append(entry)
        if level == "ERROR": results['error_logs'].append(msg)
        elif level == "SUCCESS": results['success_logs'].append(msg)
        results['all_requests_log'] = all_logs
        print(entry)
    
    log(f"🔍 STARTING REVERSE ENGINEER: {target_url}", "INFO")
    log(f"📋 Test Parameter: {test_param}", "INFO")
    
    parsed_target = urlparse(target_url)
    base_url = f"{parsed_target.scheme}://{parsed_target.netloc}"
    domain = parsed_target.netloc
    api_path = parsed_target.path
    api_query = parsed_target.query
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    session_obj = requests.Session()
    
    # ============================================
    # PHASE 1: DIRECT API DETECTION
    # ============================================
    log("=" * 50, "INFO")
    log("PHASE 1: DIRECT API DETECTION", "INFO")
    
    # Check if URL itself is an API endpoint
    api_keywords = ['/api/', '/mobile/', '/info/', '/search/', '/lookup/', '/data/', '/check/', '/verify/', '/get/', '/query/', '/fetch/', '/number/', '/v1/', '/v2/']
    
    is_api_url = any(kw in target_url.lower() for kw in api_keywords)
    
    if is_api_url:
        log("🎯 API ENDPOINT DETECTED IN URL!", "SUCCESS")
        log(f"🎯 API PATH: {api_path}", "SUCCESS")
        
        # Extract API template
        api_template = target_url
        # Replace query parameter values with placeholders
        if api_query:
            params = api_query.split('&')
            new_params = []
            for p in params:
                if '=' in p:
                    key, val = p.split('=', 1)
                    # Common parameter names to replace
                    if key.lower() in ['num', 'number', 'mobile', 'phone', 'id', 'key', 'token', 'api_key', 'apikey', 'query', 'q', 'search', 'data', 'info']:
                        new_params.append(f"{key}=PARAM")
                    else:
                        new_params.append(p)
                else:
                    new_params.append(p)
            api_template = f"{parsed_target.scheme}://{parsed_target.netloc}{api_path}?{'&'.join(new_params)}"
        else:
            api_template = target_url
        
        log(f"🎯 API TEMPLATE: {api_template}", "SUCCESS")
        results['real_api'] = api_template
        
        # Try the API with our test parameter
        test_api = api_template.replace('PARAM', test_param)
        try:
            test_resp = session_obj.get(test_api, headers=headers, timeout=10, verify=False)
            log(f"📡 Test Response: Status={test_resp.status_code}, Size={len(test_resp.text)} bytes", "SUCCESS")
            log(f"📡 Sample: {test_resp.text[:300]}", "SUCCESS")
        except Exception as e:
            log(f"❌ Test failed: {str(e)[:80]}", "ERROR")
    
    # ============================================
    # PHASE 2: DIRECT REQUEST & RESPONSE ANALYSIS
    # ============================================
    log("=" * 50, "INFO")
    log("PHASE 2: RESPONSE ANALYSIS", "INFO")
    
    try:
        resp = session_obj.get(target_url, headers=headers, timeout=20, allow_redirects=True, verify=False)
        
        log(f"📡 Response Status: {resp.status_code}", "SUCCESS")
        log(f"📡 Final URL: {resp.url}", "SUCCESS")
        log(f"📡 Content-Type: {resp.headers.get('content-type', 'unknown')}", "SUCCESS")
        log(f"📡 Response Size: {len(resp.text)} bytes", "SUCCESS")
        
        # Log ALL redirects
        for i, r in enumerate(resp.history):
            log(f"🔄 Redirect #{i+1}: {r.status_code} → {r.url}", "INFO")
        
        page_source = resp.text
        
        # ============================================
        # PHASE 3: JAVASCRIPT ANALYSIS
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 3: JAVASCRIPT ANALYSIS", "INFO")
        
        # Find JavaScript files
        js_urls = []
        
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', page_source)
        js_urls.extend(scripts)
        log(f"📁 Found {len(scripts)} <script> tags", "SUCCESS")
        
        imports = re.findall(r'import\s+.*?from\s+["\']([^"\']+)["\']', page_source)
        js_urls.extend(imports)
        
        requires = re.findall(r'require\(["\']([^"\']+)["\']\)', page_source)
        js_urls.extend(requires)
        
        next_chunks = re.findall(r'(/_next/static/[^"\'\s]+\.js)', page_source)
        js_urls.extend(next_chunks)
        
        # Make absolute URLs
        absolute_js = []
        for js in js_urls:
            if js.startswith('//'): absolute_js.append(f"https:{js}")
            elif js.startswith('/'): absolute_js.append(urljoin(base_url, js))
            elif js.startswith('http'): absolute_js.append(js)
            else: absolute_js.append(urljoin(base_url, js))
        
        absolute_js = list(set(absolute_js))
        log(f"📁 Total unique JS files: {len(absolute_js)}", "SUCCESS")
        
        # Scan JS files for API patterns
        all_api_patterns = []
        
        for js_url in absolute_js[:15]:
            try:
                log(f"🔍 Scanning: {js_url[:80]}...", "INFO")
                js_resp = session_obj.get(js_url, headers=headers, timeout=10, verify=False)
                js_content = js_resp.text
                
                # Full API URLs
                api_urls = re.findall(r'["\'\`](https?://[^"\'\`\s]{5,}?(?:api|mobile|info|search|lookup|data|get|fetch|query|backend|server|endpoint|number|check|verify)[^"\'\`\s]{0,100})["\'\`]', js_content, re.IGNORECASE)
                if api_urls:
                    log(f"   ✅ Found {len(api_urls)} API URLs", "SUCCESS")
                    all_api_patterns.extend(api_urls)
                
                # Variable assignments
                var_matches = re.findall(r'(?:const|let|var)\s+(\w*(?:API|api|BASE|base|URL|url|ENDPOINT|endpoint|BACKEND|backend|SERVER|server|HOST|host|ORIGIN|origin)\w*)\s*[=:]\s*["\'\`]([^"\'\`]+)["\'\`]', js_content, re.IGNORECASE)
                for var_name, var_value in var_matches:
                    if len(var_value) > 5 and not var_value.endswith(('.js', '.css', '.png')):
                        all_api_patterns.append(var_value)
                        log(f"   📌 {var_name} = {var_value[:100]}", "SUCCESS")
                
                # fetch/axios calls
                fetch_patterns = re.findall(r'fetch\(["\'\`]([^"\'\`]{5,})["\'\`]', js_content)
                if fetch_patterns:
                    log(f"   📡 Found {len(fetch_patterns)} fetch() calls", "SUCCESS")
                    all_api_patterns.extend(fetch_patterns)
                
                axios_patterns = re.findall(r'axios\.(?:get|post|put|delete|patch)\(["\'\`]([^"\'\`]{5,})["\'\`]', js_content)
                if axios_patterns:
                    log(f"   📡 Found {len(axios_patterns)} axios() calls", "SUCCESS")
                    all_api_patterns.extend(axios_patterns)
                
            except Exception as e:
                log(f"   ❌ Failed: {str(e)[:80]}", "ERROR")
        
        # ============================================
        # PHASE 4: HTML & CONFIG ANALYSIS
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 4: HTML & CONFIG ANALYSIS", "INFO")
        
        meta_urls = re.findall(r'<meta[^>]+(?:content|value)=["\']([^"\']*(?:api|endpoint|url|host)[^"\']*)["\']', page_source, re.IGNORECASE)
        if meta_urls:
            log(f"🏷 Found {len(meta_urls)} meta URLs", "SUCCESS")
            all_api_patterns.extend(meta_urls)
        
        data_attrs = re.findall(r'data-(?:api|url|endpoint|backend|host)=["\']([^"\']+)["\']', page_source)
        if data_attrs:
            log(f"🏷 Found {len(data_attrs)} data attributes", "SUCCESS")
            all_api_patterns.extend(data_attrs)
        
        # ============================================
        # PHASE 5: SERVERLESS FUNCTION DETECTION
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 5: SERVERLESS FUNCTION DETECTION", "INFO")
        
        serverless_paths = [
            '/api', '/api/v1', '/api/v2',
            '/api/index', '/api/index.js', '/api/index.py',
            '/api/main', '/api/main.js',
            '/api/handler', '/api/handler.js',
            '/api/app', '/api/app.js',
            '/api/number', '/api/mobile', '/api/info',
            '/api/search', '/api/lookup', '/api/data',
            '/api/check', '/api/verify', '/api/get',
            '/api/query', '/api/fetch', '/api/result',
            '/.netlify/functions/index', '/.netlify/functions/api',
            '/api/hello', '/api/test', '/api/health',
        ]
        
        for path in serverless_paths:
            test_url = f"{base_url}{path}"
            try:
                test_resp = session_obj.get(test_url, headers=headers, timeout=5, verify=False)
                
                if test_resp.status_code != 404:
                    content = test_resp.text[:300]
                    ct = test_resp.headers.get('content-type', '')
                    
                    if 'json' in ct or content.strip().startswith(('{', '[')):
                        log(f"✅ [{test_resp.status_code}] {test_url}", "SUCCESS")
                        all_api_patterns.append(test_url)
                        log(f"   Sample: {content[:150]}", "INFO")
            except:
                pass
        
        # ============================================
        # PHASE 6: ENVIRONMENT PROBING
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 6: ENVIRONMENT PROBING", "INFO")
        
        env_files = ['/.env', '/.env.local', '/package.json', '/vercel.json', '/netlify.toml', '/next.config.js']
        
        for env_file in env_files:
            test_url = f"{base_url}{env_file}"
            try:
                test_resp = session_obj.get(test_url, headers=headers, timeout=5, verify=False)
                if test_resp.status_code == 200:
                    log(f"📄 Found: {env_file} ({len(test_resp.text)} bytes)", "SUCCESS")
                    
                    config_urls = re.findall(r'["\'](https?://[^"\']{5,}(?:api|mobile|backend|server|endpoint)[^"\']{0,50})["\']', test_resp.text, re.IGNORECASE)
                    if config_urls:
                        log(f"   🔗 Found {len(config_urls)} API URLs", "SUCCESS")
                        all_api_patterns.extend(config_urls)
                    
                    env_apis = re.findall(r'(?:API|BASE|BACKEND|SERVER|ENDPOINT)\w*\s*=\s*["\']?([^"\'\n\r]{5,})["\']?', test_resp.text, re.IGNORECASE)
                    if env_apis:
                        log(f"   🔑 Found {len(env_apis)} env API vars", "SUCCESS")
                        all_api_patterns.extend(env_apis)
            except:
                pass
        
        # ============================================
        # PHASE 7: CLEAN & IDENTIFY REAL API
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 7: IDENTIFYING REAL API", "INFO")
        
        # Clean patterns
        clean_apis = []
        for api in all_api_patterns:
            api = api.strip().strip('"').strip("'").strip('`')
            if api and len(api) > 5:
                if not any(skip in api.lower() for skip in ['.js', '.css', '.png', '.jpg', '.svg', 'localhost', '127.0.0.1']):
                    if 'http' in api or api.startswith('/'):
                        clean_apis.append(api)
        
        clean_apis = list(set(clean_apis))
        log(f"📊 Total unique API candidates: {len(clean_apis)}", "SUCCESS")
        results['all_apis_found'] = clean_apis
        
        # Filter backend APIs
        backend_apis = []
        for api in clean_apis:
            try:
                if api.startswith('http'):
                    if urlparse(api).netloc != domain:
                        backend_apis.append(api)
                else:
                    backend_apis.append(api)
            except:
                backend_apis.append(api)
        
        keyword_apis = []
        for api in backend_apis:
            api_lower = api.lower()
            if any(kw in api_lower for kw in ['api', 'mobile', 'info', 'search', 'lookup', 'data', 'number']):
                keyword_apis.append(api)
        
        # ============================================
        # PHASE 8: TEST CANDIDATES
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 8: TESTING CANDIDATES", "INFO")
        
        tested_apis = []
        
        # If we didn't find API from URL, test candidates
        if not results['real_api']:
            test_candidates = (keyword_apis or backend_apis or clean_apis)[:15]
            
            for candidate in test_candidates:
                try:
                    test_url = candidate if candidate.startswith('http') else urljoin(base_url, candidate)
                    
                    for param_name in ['num', 'number', 'mobile', 'phone', 'id', 'query', 'q']:
                        test_full = f"{test_url}?{param_name}={test_param}"
                        try:
                            test_resp = session_obj.get(test_full, headers=headers, timeout=10, verify=False)
                            
                            if test_resp.status_code == 200 and len(test_resp.text) > 30:
                                tested_apis.append({
                                    'url': candidate,
                                    'test_url': test_full,
                                    'status': test_resp.status_code,
                                    'size': len(test_resp.text),
                                    'sample': test_resp.text[:300]
                                })
                                
                                log(f"✅ [{test_resp.status_code}] {test_full} ({len(test_resp.text)} bytes)", "SUCCESS")
                                
                                if results['real_api'] is None:
                                    results['real_api'] = candidate
                                    log(f"🎯 REAL API IDENTIFIED: {candidate}", "SUCCESS")
                                break
                        except:
                            pass
                except:
                    pass
        
        results['tested_apis'] = tested_apis
        
        log(f"🏁 REVERSE ENGINEERING COMPLETE", "SUCCESS")
        log(f"🎯 REAL API: {results['real_api'] or 'NOT FOUND'}", "SUCCESS" if results['real_api'] else "WARNING")
        
    except Exception as e:
        log(f"💥 CRITICAL ERROR: {str(e)}", "ERROR")
        results['error'] = str(e)
    
    results['all_logs'] = all_logs
    return results

# ============================================
# 🎨 UI
# ============================================
LOGIN_PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>💀 API REVERSE ENGINEER v4</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:system-ui}
.bg{position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(circle,rgba(255,0,0,0.03) 1px,transparent 1px);background-size:30px 30px;animation:bg 15s linear infinite}
@keyframes bg{0%{transform:translate(0)}100%{transform:translate(30px,30px)}}
.box{background:rgba(10,0,0,0.97);padding:45px;border-radius:18px;border:2px solid #f00;width:400px;text-align:center;z-index:1;box-shadow:0 0 60px rgba(255,0,0,0.3);position:relative}
h1{color:#f00;font-size:1.5em;letter-spacing:2px}
.tag{color:#888;font-size:0.6em;letter-spacing:3px;margin:8px 0 20px}
input{width:100%;padding:14px;background:#000;border:1px solid #f00;border-radius:10px;color:#f44;margin:8px 0;font-size:14px;font-family:monospace}
input:focus{border-color:#0f0;outline:none}
.btn{width:100%;padding:14px;background:#c00;color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:15px;margin-top:10px;letter-spacing:2px}
.btn:hover{background:#f00}
</style></head><body>
<div class="bg"></div>
<div class="box">
<h1>💀 API REVERSE ENGINEER</h1>
<div class="tag">v4.0 • 100% REAL API</div>
<form method="post">
<input type="text" name="user" placeholder="🔑 USERNAME" autocomplete="off">
<input type="password" name="pass" placeholder="🔐 PASSWORD">
<button class="btn" type="submit">☠️ ACCESS</button>
</form>
{% if error %}<p style="color:#f00;margin-top:8px">{{ error }}</p>{% endif %}
</div>
</body></html>"""

DASHBOARD = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>💀 API REVERSE ENGINEER v4</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#ddd;font-family:system-ui;padding:10px}
.container{max-width:1100px;margin:0 auto}
.header{display:flex;justify-content:space-between;align-items:center;padding:15px;border:2px solid #f00;border-radius:12px;margin-bottom:12px;background:#0a0000}
.header h1{color:#f00;font-size:1.2em}
.card{background:#0a0000;border:1px solid #300;border-radius:12px;padding:16px;margin-bottom:10px}
.card h3{color:#f44;margin-bottom:10px;font-size:0.8em}
input,textarea{width:100%;padding:10px;background:#000;border:1px solid #f00;border-radius:8px;color:#f44;margin:4px 0;font-size:12px;font-family:monospace}
label{font-size:0.55em;color:#888;display:block;margin-top:5px}
.btn{width:100%;padding:12px;background:#c00;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;margin:3px 0;font-size:0.7em}
.btn:hover{background:#f00}
.btn-green{background:#0a0}.btn-green:hover{background:#0f0}
.btn-yellow{background:#f80;color:#000}.btn-yellow:hover{background:#ff0}
.result-box{background:#000;border:1px solid #0f0;border-radius:8px;padding:10px;max-height:500px;overflow:auto;font-family:monospace;font-size:0.6em;color:#0f0;white-space:pre-wrap;word-break:break-all;margin-top:6px}
.real-api-box{background:rgba(0,255,0,0.05);border:2px solid #0f0;padding:12px;border-radius:8px;text-align:center;margin:6px 0;font-size:0.75em;color:#0f0;word-break:break-all}
.badge{display:inline-block;padding:3px 8px;border-radius:8px;font-size:0.5em;font-weight:700}
.badge-on{background:rgba(0,255,0,0.1);color:#0f0;border:1px solid rgba(0,255,0,0.2)}
.copy-btn{padding:3px 8px;background:#333;color:#ff0;border:1px solid #ff0;border-radius:4px;cursor:pointer;font-size:0.5em}
</style></head><body>
<div class="container">
<div class="header">
<div><h1>💀 API REVERSE ENGINEER v4.0</h1><div style="color:#888;font-size:0.45em">100% REAL API CAPTURE • ALL LOGS VISIBLE</div></div>
<div style="display:flex;gap:8px;align-items:center">
<span class="badge badge-on">v4.0</span>
<a href="/logout" style="color:#f00;text-decoration:none;font-size:0.55em">EXIT</a>
</div>
</div>

<div class="card">
<h3>🎯 ENTER URL</h3>
<label>Website or API URL</label>
<input type="text" id="targetUrl" placeholder="https://example.vercel.app/api/number?num=123" value="{{ last_url }}">
<label>Test Parameter</label>
<input type="text" id="testParam" placeholder="9876543210" value="{{ last_param }}">
<button class="btn" onclick="startScan()">🔍 START SCAN</button>
<div class="result-box" id="progress" style="max-height:200px;color:#ff0">💀 Ready. Enter URL and click START SCAN...</div>
</div>

<div class="card">
<h3>🎯 REAL API FOUND</h3>
<div class="real-api-box" id="realAPI">Waiting for scan...</div>
<button class="btn btn-green" onclick="copyRealAPI()">📋 COPY REAL API</button>
<button class="btn btn-yellow" onclick="testRealAPI()">🧪 TEST REAL API</button>
<div class="result-box" id="testResult" style="max-height:150px;display:none;margin-top:6px"></div>
</div>

<div class="card">
<h3>📋 COMPLETE SCAN LOGS</h3>
<div class="result-box" id="fullLogs" style="max-height:400px">
<p style="color:#555;font-size:0.6em">All scan logs appear here in real-time...</p>
</div>
</div>
</div>

<script>
var realAPI = '';
var scanInterval = null;

function copyRealAPI() {
    if (realAPI) {
        navigator.clipboard.writeText(realAPI);
        alert('✅ REAL API COPIED!\\n\\n' + realAPI);
    } else {
        alert('⚠ No API found yet!');
    }
}

function testRealAPI() {
    if (!realAPI) { alert('⚠ No API found!'); return; }
    var param = document.getElementById('testParam').value.trim() || '9876543210';
    var testUrl = realAPI.replace('PARAM', param);
    
    document.getElementById('testResult').style.display = 'block';
    document.getElementById('testResult').textContent = '⏳ Testing: ' + testUrl;
    
    fetch('/test_api', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url: testUrl})
    })
    .then(r => r.json())
    .then(d => {
        if (d.success) {
            document.getElementById('testResult').textContent = '✅ SUCCESS!\\nStatus: ' + d.status + '\\nSize: ' + d.size + ' bytes\\n\\n' + d.sample;
            document.getElementById('testResult').style.color = '#0f0';
        } else {
            document.getElementById('testResult').textContent = '❌ FAILED\\n' + d.error;
            document.getElementById('testResult').style.color = '#f00';
        }
    });
}

function startScan() {
    var url = document.getElementById('targetUrl').value.trim();
    var param = document.getElementById('testParam').value.trim() || '9876543210';
    
    if (!url) { alert('Enter URL!'); return; }
    if (!url.startsWith('http')) url = 'https://' + url;
    
    document.getElementById('progress').textContent = '⏳ INITIALIZING SCAN...';
    document.getElementById('progress').style.color = '#ff0';
    
    if (scanInterval) clearInterval(scanInterval);
    
    fetch('/start_scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url: url, param: param})
    })
    .then(r => r.json())
    .then(d => {
        if (d.scan_id) {
            var scanId = d.scan_id;
            scanInterval = setInterval(function() {
                fetch('/scan_logs?scan_id=' + scanId)
                .then(r => r.json())
                .then(logData => {
                    if (logData.logs && logData.logs.length > 0) {
                        document.getElementById('progress').textContent = logData.logs.join('\\n');
                        document.getElementById('progress').scrollTop = document.getElementById('progress').scrollHeight;
                        document.getElementById('fullLogs').textContent = logData.logs.join('\\n');
                        document.getElementById('fullLogs').scrollTop = document.getElementById('fullLogs').scrollHeight;
                        
                        if (logData.complete) {
                            clearInterval(scanInterval);
                            document.getElementById('progress').style.color = '#0f0';
                            
                            if (logData.real_api) {
                                realAPI = logData.real_api;
                                document.getElementById('realAPI').textContent = logData.real_api;
                                document.getElementById('realAPI').style.color = '#0f0';
                            } else {
                                document.getElementById('realAPI').textContent = '⚠ API not found. Check logs.';
                                document.getElementById('realAPI').style.color = '#f80';
                            }
                        }
                    }
                });
            }, 500);
        }
    });
}
</script></body></html>"""

# ============================================
# STORAGE
# ============================================
scan_storage = {}

# ============================================
# ROUTES
# ============================================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('user') == ADMIN_USER and request.form.get('pass') == ADMIN_PASS:
            session['auth'] = True
            return redirect('/dashboard')
        return render_template_string(LOGIN_PAGE, error="ACCESS DENIED")
    return render_template_string(LOGIN_PAGE, error=None)

@app.route('/dashboard')
def dashboard():
    if not session.get('auth'): return redirect('/')
    return render_template_string(DASHBOARD,
        last_url=session.get('last_url', ''),
        last_param=session.get('last_param', ''))

@app.route('/start_scan', methods=['POST'])
def start_scan():
    if not session.get('auth'): return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    url = data.get('url', '')
    param = data.get('param', '9876543210')
    
    if not url: return jsonify({'error': 'URL required'})
    
    session['last_url'] = url
    session['last_param'] = param
    
    import uuid, threading
    
    scan_id = str(uuid.uuid4())[:8]
    
    scan_storage[scan_id] = {
        'logs': [f'🔍 Starting scan: {url}'],
        'complete': False,
        'real_api': None
    }
    
    def run_scan():
        results = reverse_engineer_api(url, param)
        scan_storage[scan_id]['logs'] = results.get('all_logs', [])
        scan_storage[scan_id]['complete'] = True
        scan_storage[scan_id]['real_api'] = results.get('real_api')
        
        if results.get('real_api'):
            if 'discovered_apis' not in session:
                session['discovered_apis'] = []
            session['discovered_apis'].insert(0, results['real_api'])
    
    t = threading.Thread(target=run_scan, daemon=True)
    t.start()
    
    return jsonify({'scan_id': scan_id})

@app.route('/scan_logs')
def scan_logs():
    scan_id = request.args.get('scan_id', '')
    if scan_id in scan_storage:
        d = scan_storage[scan_id]
        return jsonify({'logs': d['logs'], 'complete': d['complete'], 'real_api': d['real_api']})
    return jsonify({'logs': ['Scan not found'], 'complete': False})

@app.route('/test_api', methods=['POST'])
def test_api():
    if not session.get('auth'): return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    url = data.get('url', '')
    
    if not url: return jsonify({'success': False, 'error': 'URL required'})
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0'}
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        return jsonify({
            'success': True,
            'status': resp.status_code,
            'size': len(resp.text),
            'sample': resp.text[:500]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)[:200]})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    print("💀 API REVERSE ENGINEER v4.0")
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
