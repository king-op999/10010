from flask import Flask, request, jsonify, render_template_string, session, redirect
import requests
import re
import json
from urllib.parse import urlparse, urljoin
import urllib3
urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = 'bronx_reverse_engineer_2024'

ADMIN_USER = "bronx"
ADMIN_PASS = "ultra2026"

# ============================================
# 💀 ULTIMATE API REVERSE ENGINEER
# ============================================
def reverse_engineer_api(target_url, test_param="9876543210"):
    """
    ULTIMATE API FINDER - Works on ANY website/API type
    """
    all_logs = []  # EVERYTHING is logged
    results = {
        'original_url': target_url,
        'real_api': None,
        'all_apis_found': [],
        'all_requests_log': [],
        'error_logs': [],
        'success_logs': []
    }
    
    def log(msg, level="INFO"):
        """Log EVERYTHING - no data lost"""
        entry = f"[{level}] {msg}"
        all_logs.append(entry)
        if level == "ERROR":
            results['error_logs'].append(msg)
        elif level == "SUCCESS":
            results['success_logs'].append(msg)
        results['all_requests_log'].append(entry)
        print(entry)  # Also print to console
    
    log(f"🔍 STARTING REVERSE ENGINEER: {target_url}", "INFO")
    log(f"📋 Test Parameter: {test_param}", "INFO")
    
    parsed_target = urlparse(target_url)
    base_url = f"{parsed_target.scheme}://{parsed_target.netloc}"
    domain = parsed_target.netloc
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    # ============================================
    # PHASE 1: Direct Request & Response Analysis
    # ============================================
    log("=" * 50, "INFO")
    log("PHASE 1: DIRECT REQUEST ANALYSIS", "INFO")
    
    try:
        session = requests.Session()
        resp = session.get(target_url, headers=headers, timeout=20, allow_redirects=True, verify=False)
        
        log(f"📡 Response Status: {resp.status_code}", "SUCCESS")
        log(f"📡 Final URL: {resp.url}", "SUCCESS")
        log(f"📡 Content-Type: {resp.headers.get('content-type', 'unknown')}", "SUCCESS")
        log(f"📡 Response Size: {len(resp.text)} bytes", "SUCCESS")
        
        # Log ALL redirects
        for i, r in enumerate(resp.history):
            log(f"🔄 Redirect #{i+1}: {r.status_code} → {r.url}", "INFO")
        
        # Log ALL response headers
        log("📋 RESPONSE HEADERS:", "INFO")
        for key, value in resp.headers.items():
            log(f"   {key}: {value}", "INFO")
        
        page_source = resp.text
        
        # ============================================
        # PHASE 2: JavaScript Analysis
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 2: JAVASCRIPT ANALYSIS", "INFO")
        
        # Find ALL JavaScript files
        js_urls = []
        
        # <script src="...">
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', page_source)
        js_urls.extend(scripts)
        log(f"📁 Found {len(scripts)} <script> tags", "SUCCESS")
        
        # import statements
        imports = re.findall(r'import\s+.*?from\s+["\']([^"\']+)["\']', page_source)
        js_urls.extend(imports)
        log(f"📁 Found {len(imports)} import statements", "SUCCESS")
        
        # require() calls
        requires = re.findall(r'require\(["\']([^"\']+)["\']\)', page_source)
        js_urls.extend(requires)
        log(f"📁 Found {len(requires)} require() calls", "SUCCESS")
        
        # Next.js chunks
        next_chunks = re.findall(r'(/_next/static/[^"\'\s]+\.js)', page_source)
        js_urls.extend(next_chunks)
        log(f"📁 Found {len(next_chunks)} Next.js chunks", "SUCCESS")
        
        # Make absolute URLs
        absolute_js = []
        for js in js_urls:
            if js.startswith('//'):
                absolute_js.append(f"https:{js}")
            elif js.startswith('/'):
                absolute_js.append(urljoin(base_url, js))
            elif js.startswith('http'):
                absolute_js.append(js)
            else:
                absolute_js.append(urljoin(base_url, js))
        
        absolute_js = list(set(absolute_js))
        log(f"📁 Total unique JS files: {len(absolute_js)}", "SUCCESS")
        
        # Scan EACH JS file for API patterns
        all_api_patterns = []
        
        for js_url in absolute_js[:20]:  # Scan up to 20 JS files
            try:
                log(f"🔍 Scanning: {js_url[:80]}...", "INFO")
                js_resp = session.get(js_url, headers=headers, timeout=10, verify=False)
                js_content = js_resp.text
                
                # Pattern 1: Full API URLs
                api_urls = re.findall(r'["\'\`](https?://[^"\'\`\s]{5,}?(?:api|mobile|info|search|lookup|data|get|fetch|query|backend|server|endpoint|number|check|verify)[^"\'\`\s]{0,100})["\'\`]', js_content, re.IGNORECASE)
                if api_urls:
                    log(f"   ✅ Found {len(api_urls)} API URLs", "SUCCESS")
                    all_api_patterns.extend(api_urls)
                
                # Pattern 2: Variable assignments
                var_patterns = [
                    r'(?:const|let|var)\s+(\w*(?:API|api|BASE|base|URL|url|ENDPOINT|endpoint|BACKEND|backend|SERVER|server|HOST|host|ORIGIN|origin)\w*)\s*[=:]\s*["\'\`]([^"\'\`]+)["\'\`]',
                    r'(\w*(?:API|api|BASE|base|URL|url|ENDPOINT|endpoint))\s*:\s*["\'\`]([^"\'\`]+)["\'\`]',
                ]
                
                for vp in var_patterns:
                    var_matches = re.findall(vp, js_content, re.IGNORECASE)
                    for var_name, var_value in var_matches:
                        if len(var_value) > 5 and not var_value.endswith(('.js', '.css', '.png', '.jpg')):
                            all_api_patterns.append(var_value)
                            log(f"   📌 {var_name} = {var_value[:100]}", "SUCCESS")
                
                # Pattern 3: fetch/axios calls
                fetch_patterns = re.findall(r'fetch\(["\'\`]([^"\'\`]{5,})["\'\`]', js_content)
                if fetch_patterns:
                    log(f"   📡 Found {len(fetch_patterns)} fetch() calls", "SUCCESS")
                    all_api_patterns.extend(fetch_patterns)
                
                axios_patterns = re.findall(r'axios\.(?:get|post|put|delete|patch)\(["\'\`]([^"\'\`]{5,})["\'\`]', js_content)
                if axios_patterns:
                    log(f"   📡 Found {len(axios_patterns)} axios() calls", "SUCCESS")
                    all_api_patterns.extend(axios_patterns)
                
                # Pattern 4: Proxy/rewrite configs
                proxy_matches = re.findall(r'["\']proxy["\']\s*:\s*["\']([^"\']{5,})["\']', js_content)
                if proxy_matches:
                    log(f"   🔄 Found {len(proxy_matches)} proxy configs", "SUCCESS")
                    all_api_patterns.extend(proxy_matches)
                
            except Exception as e:
                log(f"   ❌ Failed: {str(e)[:80]}", "ERROR")
        
        # ============================================
        # PHASE 3: HTML Meta & Config Analysis
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 3: HTML & CONFIG ANALYSIS", "INFO")
        
        # Meta tags with URLs
        meta_urls = re.findall(r'<meta[^>]+(?:content|value)=["\']([^"\']*(?:api|endpoint|url|host)[^"\']*)["\']', page_source, re.IGNORECASE)
        if meta_urls:
            log(f"🏷 Found {len(meta_urls)} meta URLs", "SUCCESS")
            all_api_patterns.extend(meta_urls)
        
        # Data attributes
        data_attrs = re.findall(r'data-(?:api|url|endpoint|backend|host)=["\']([^"\']+)["\']', page_source)
        if data_attrs:
            log(f"🏷 Found {len(data_attrs)} data attributes", "SUCCESS")
            all_api_patterns.extend(data_attrs)
        
        # Inline JSON configs
        json_configs = re.findall(r'(?:config|settings|env)\s*=\s*({[^}]+})', page_source, re.IGNORECASE)
        for jc in json_configs:
            try:
                urls_in_json = re.findall(r'["\']([^"\']*(?:api|url|endpoint|host)[^"\']*)["\']', jc, re.IGNORECASE)
                all_api_patterns.extend(urls_in_json)
            except:
                pass
        
        # ============================================
        # PHASE 4: Serverless Function Detection
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 4: SERVERLESS FUNCTION DETECTION", "INFO")
        
        serverless_paths = [
            '/api', '/api/v1', '/api/v2',
            '/api/index', '/api/index.js', '/api/index.py', '/api/index.ts',
            '/api/main', '/api/main.js', '/api/main.py',
            '/api/handler', '/api/handler.js',
            '/api/app', '/api/app.js',
            '/api/server', '/api/server.js',
            '/api/number', '/api/mobile', '/api/info',
            '/api/search', '/api/lookup', '/api/data',
            '/api/check', '/api/verify', '/api/get',
            '/api/query', '/api/fetch', '/api/result',
            '/.netlify/functions/index', '/.netlify/functions/api',
            '/.netlify/functions/main', '/.netlify/functions/handler',
            '/api/hello', '/api/test', '/api/health',
            '/api/v1/search', '/api/v1/data', '/api/v1/info',
        ]
        
        for path in serverless_paths:
            test_url = f"{base_url}{path}"
            try:
                test_resp = session.get(test_url, headers=headers, timeout=8, verify=False)
                
                if test_resp.status_code != 404:
                    log(f"✅ [{test_resp.status_code}] {test_url} - Content-Type: {test_resp.headers.get('content-type', '?')}", "SUCCESS")
                    
                    # Check if response looks like API
                    content = test_resp.text[:500]
                    is_api = False
                    
                    # Check content type
                    ct = test_resp.headers.get('content-type', '')
                    if 'json' in ct or 'xml' in ct:
                        is_api = True
                    
                    # Check if starts with JSON
                    if content.strip().startswith(('{', '[', '<')):
                        is_api = True
                    
                    if is_api:
                        log(f"🎯 LIKELY API ENDPOINT: {test_url}", "SUCCESS")
                        all_api_patterns.append(test_url)
                    
                    # Log sample response
                    log(f"   Sample: {content[:200]}", "INFO")
                    
            except Exception as e:
                pass  # Expected for non-existent paths
        
        # ============================================
        # PHASE 5: Environment & Config Probing
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 5: ENVIRONMENT PROBING", "INFO")
        
        env_files = [
            '/.env', '/.env.local', '/.env.production', '/.env.development',
            '/env.json', '/config.json', '/settings.json',
            '/package.json', '/vercel.json', '/netlify.toml',
            '/next.config.js', '/next.config.mjs',
            '/app.config.js', '/app.config.json',
        ]
        
        for env_file in env_files:
            test_url = f"{base_url}{env_file}"
            try:
                test_resp = session.get(test_url, headers=headers, timeout=5, verify=False)
                if test_resp.status_code == 200:
                    log(f"📄 Found: {env_file} ({len(test_resp.text)} bytes)", "SUCCESS")
                    
                    # Search for API URLs in config
                    config_urls = re.findall(r'["\'](https?://[^"\']{5,}(?:api|mobile|backend|server|endpoint)[^"\']{0,50})["\']', test_resp.text, re.IGNORECASE)
                    if config_urls:
                        log(f"   🔗 Found {len(config_urls)} API URLs", "SUCCESS")
                        all_api_patterns.extend(config_urls)
                    
                    # Environment variables with API patterns
                    env_apis = re.findall(r'(?:API|BASE|BACKEND|SERVER|ENDPOINT)\w*\s*=\s*["\']?([^"\'\n\r]{5,})["\']?', test_resp.text, re.IGNORECASE)
                    if env_apis:
                        log(f"   🔑 Found {len(env_apis)} env API vars", "SUCCESS")
                        all_api_patterns.extend(env_apis)
            except:
                pass
        
        # ============================================
        # PHASE 6: Clean & Identify Real API
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 6: IDENTIFYING REAL API", "INFO")
        
        # Clean patterns
        clean_apis = []
        for api in all_api_patterns:
            api = api.strip().strip('"').strip("'").strip('`').strip()
            
            # Skip non-API patterns
            if not api or len(api) < 5:
                continue
            if any(skip in api.lower() for skip in ['.js', '.css', '.png', '.jpg', '.svg', '.woff', '.ico', 'localhost', '127.0.0.1']):
                continue
            if api.count('/') < 1:
                continue
            
            clean_apis.append(api)
        
        clean_apis = list(set(clean_apis))
        log(f"📊 Total unique API candidates: {len(clean_apis)}", "SUCCESS")
        
        # Filter: APIs that are DIFFERENT from target domain (backend)
        backend_apis = []
        for api in clean_apis:
            try:
                if api.startswith('http'):
                    api_domain = urlparse(api).netloc
                    if api_domain != domain:
                        backend_apis.append(api)
                else:
                    backend_apis.append(api)
            except:
                backend_apis.append(api)
        
        # Filter: APIs containing common keywords
        keyword_apis = []
        api_keywords = ['api', 'mobile', 'info', 'search', 'lookup', 'data', 'number', 'check', 'verify', 'get', 'query', 'fetch']
        for api in backend_apis:
            api_lower = api.lower()
            if any(kw in api_lower for kw in api_keywords):
                keyword_apis.append(api)
        
        # ============================================
        # PHASE 7: Test Candidates
        # ============================================
        log("=" * 50, "INFO")
        log("PHASE 7: TESTING CANDIDATES", "INFO")
        
        tested_apis = []
        real_api = None
        
        test_candidates = (keyword_apis or backend_apis or clean_apis)[:20]
        
        for candidate in test_candidates:
            try:
                # Build test URL with parameter
                test_url = candidate
                if not test_url.startswith('http'):
                    test_url = urljoin(base_url, candidate)
                
                if '?' not in test_url:
                    for param_name in ['num', 'number', 'mobile', 'phone', 'id', 'query', 'q', 'search']:
                        test_full = f"{test_url}?{param_name}={test_param}"
                        try:
                            test_resp = session.get(test_full, headers=headers, timeout=10, verify=False)
                            
                            if test_resp.status_code == 200 and len(test_resp.text) > 30:
                                tested_apis.append({
                                    'url': candidate,
                                    'test_url': test_full,
                                    'status': test_resp.status_code,
                                    'size': len(test_resp.text),
                                    'content_type': test_resp.headers.get('content-type', '?'),
                                    'sample': test_resp.text[:300]
                                })
                                
                                log(f"✅ [{test_resp.status_code}] {test_full} ({len(test_resp.text)} bytes)", "SUCCESS")
                                
                                # This is the REAL API!
                                if real_api is None:
                                    real_api = candidate
                                    log(f"🎯 REAL API IDENTIFIED: {candidate}", "SUCCESS")
                                break
                        except:
                            pass
            except:
                pass
        
        results['real_api'] = real_api
        results['all_apis_found'] = clean_apis
        results['tested_apis'] = tested_apis
        results['complete_logs'] = all_logs
        
        log(f"🏁 REVERSE ENGINEERING COMPLETE", "SUCCESS")
        log(f"🎯 REAL API: {real_api or 'NOT FOUND'}", "SUCCESS" if real_api else "WARNING")
        
    except Exception as e:
        log(f"💥 CRITICAL ERROR: {str(e)}", "ERROR")
        results['error'] = str(e)
    
    results['all_logs'] = all_logs
    return results

# ============================================
# 🎨 UI
# ============================================
LOGIN_PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>💀 API REVERSE ENGINEER</title>
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
<div class="tag">ULTIMATE • 100% REAL API</div>
<form method="post">
<input type="text" name="user" placeholder="🔑 USERNAME" autocomplete="off">
<input type="password" name="pass" placeholder="🔐 PASSWORD">
<button class="btn" type="submit">☠️ ACCESS</button>
</form>
{% if error %}<p style="color:#f00;margin-top:8px">{{ error }}</p>{% endif %}
</div>
</body></html>"""

DASHBOARD = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>💀 API REVERSE ENGINEER</title>
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
<div><h1>💀 API REVERSE ENGINEER v3.0</h1><div style="color:#888;font-size:0.45em">100% REAL API • ALL LOGS • NO DATA LOST</div></div>
<div style="display:flex;gap:8px;align-items:center">
<span class="badge badge-on">ULTIMATE</span>
<a href="/logout" style="color:#f00;text-decoration:none;font-size:0.55em">EXIT</a>
</div>
</div>

<div class="card">
<h3>🎯 TARGET URL</h3>
<label>Website/API URL</label>
<input type="text" id="targetUrl" placeholder="https://example.vercel.app" value="{{ last_url }}">
<label>Test Parameter (number/ID)</label>
<input type="text" id="testParam" placeholder="9876543210" value="{{ last_param }}">
<button class="btn" onclick="startScan()">🔍 START REVERSE ENGINEERING</button>
<div class="result-box" id="progress" style="max-height:200px;color:#ff0">💀 Ready. Enter URL and click button...</div>
</div>

<div class="card">
<h3>🎯 REAL API FOUND</h3>
<div class="real-api-box" id="realAPI">Waiting for scan...</div>
<button class="btn btn-green" onclick="copyRealAPI()">📋 COPY REAL API</button>
</div>

<div class="card">
<h3>📋 COMPLETE SCAN LOGS (No data lost)</h3>
<div class="result-box" id="fullLogs" style="max-height:400px">
<p style="color:#555;font-size:0.6em">All scan logs will appear here in real-time...</p>
</div>
</div>
</div>

<script>
var realAPI = '';
var scanInterval = null;

function copyRealAPI() {
    if (realAPI) {
        navigator.clipboard.writeText(realAPI);
        alert('✅ REAL API COPIED!\\n' + realAPI);
    } else {
        alert('⚠ No API found yet! Run scan first.');
    }
}

function startScan() {
    var url = document.getElementById('targetUrl').value.trim();
    var param = document.getElementById('testParam').value.trim() || '9876543210';
    
    if (!url) { alert('Enter URL!'); return; }
    if (!url.startsWith('http')) url = 'https://' + url;
    
    document.getElementById('progress').textContent = '⏳ INITIALIZING SCAN...';
    document.getElementById('progress').style.color = '#ff0';
    
    if (scanInterval) clearInterval(scanInterval);
    
    // Start scan
    fetch('/start_scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url: url, param: param})
    })
    .then(r => r.json())
    .then(d => {
        if (d.scan_id) {
            // Poll for logs
            var scanId = d.scan_id;
            scanInterval = setInterval(function() {
                fetch('/scan_logs?scan_id=' + scanId)
                .then(r => r.json())
                .then(logData => {
                    if (logData.logs) {
                        document.getElementById('progress').textContent = logData.logs.join('\\n');
                        document.getElementById('progress').scrollTop = document.getElementById('progress').scrollHeight;
                        
                        if (logData.complete) {
                            clearInterval(scanInterval);
                            document.getElementById('progress').style.color = '#0f0';
                            
                            if (logData.real_api) {
                                realAPI = logData.real_api;
                                document.getElementById('realAPI').textContent = logData.real_api;
                                document.getElementById('realAPI').style.color = '#0f0';
                            }
                            
                            // Show full logs
                            fetch('/full_logs?scan_id=' + scanId)
                            .then(r => r.json())
                            .then(fullData => {
                                if (fullData.logs) {
                                    document.getElementById('fullLogs').textContent = fullData.logs.join('\\n');
                                }
                            });
                        }
                    }
                });
            }, 500);
        }
    });
}
</script></body></html>"""

# ============================================
# STORAGE FOR SCANS
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
    
    import uuid
    import threading
    
    scan_id = str(uuid.uuid4())[:8]
    
    # Initialize storage
    scan_storage[scan_id] = {
        'logs': ['🔍 Starting scan for: ' + url],
        'complete': False,
        'real_api': None
    }
    
    # Run scan in background
    def run_scan():
        results = reverse_engineer_api(url, param)
        
        # Store ALL logs
        scan_storage[scan_id]['logs'] = results.get('all_logs', results.get('all_requests_log', []))
        scan_storage[scan_id]['complete'] = True
        scan_storage[scan_id]['real_api'] = results.get('real_api')
        
        # Save to session
        if results.get('real_api'):
            if 'discovered_apis' not in session:
                session['discovered_apis'] = []
            if results['real_api'] not in session['discovered_apis']:
                session['discovered_apis'].insert(0, results['real_api'])
    
    t = threading.Thread(target=run_scan, daemon=True)
    t.start()
    
    return jsonify({'scan_id': scan_id, 'status': 'started'})

@app.route('/scan_logs')
def scan_logs():
    scan_id = request.args.get('scan_id', '')
    if scan_id in scan_storage:
        data = scan_storage[scan_id]
        return jsonify({
            'logs': data['logs'],
            'complete': data['complete'],
            'real_api': data['real_api']
        })
    return jsonify({'logs': ['Scan not found'], 'complete': False})

@app.route('/full_logs')
def full_logs():
    scan_id = request.args.get('scan_id', '')
    if scan_id in scan_storage:
        return jsonify({'logs': scan_storage[scan_id]['logs']})
    return jsonify({'logs': ['No logs']})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    print("💀 API REVERSE ENGINEER v3.0 ULTIMATE")
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
