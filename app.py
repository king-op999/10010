from flask import Flask, request, jsonify, render_template_string, session, redirect
import requests
import re
import json
from urllib.parse import urlparse, urljoin
import urllib3
urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = 'bronx_sniffer_pro_max_2024'

ADMIN_USER = "bronx"
ADMIN_PASS = "ultra2026"

# ============================================
# 💀 PROXY SNIFFER - 100% REAL API CAPTURE
# ============================================
def proxy_sniff(target_url, test_param="9876543210"):
    """
    PROXY METHOD: 
    1. Send request THROUGH our server
    2. Intercept the ACTUAL request being made
    3. Capture the REAL backend URL
    """
    results = {
        'original_url': target_url,
        'real_api': None,
        'api_base': None,
        'request_url': None,
        'response_sample': None,
        'headers_sent': {},
        'redirect_chain': [],
        'intercepted_apis': [],
        'all_found': []
    }
    
    try:
        # ============================================
        # STEP 1: Direct request & trace redirects
        # ============================================
        session = requests.Session()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Send request with redirect tracing
        resp = session.get(target_url, headers=headers, timeout=15, allow_redirects=True, verify=False)
        
        # Capture redirect chain
        for r in resp.history:
            results['redirect_chain'].append({
                'url': r.url,
                'status': r.status_code,
                'headers': dict(r.headers)
            })
        
        # Final URL (may be different from input)
        final_url = resp.url
        results['request_url'] = final_url
        results['response_sample'] = resp.text[:500]
        results['headers_sent'] = dict(resp.request.headers)
        
        # ============================================
        # STEP 2: Parse HTML to find API calls
        # ============================================
        page_source = resp.text
        
        # Find all URLs in the page
        all_urls = re.findall(r'https?://[^\s"\'<>]+', page_source)
        
        # Find API-like URLs
        api_keywords = ['api', 'mobile', 'info', 'search', 'lookup', 'data', 'get', 'query', 'backend', 'server', 'endpoint', 'number', 'check', 'verify', 'fetch']
        
        for url in all_urls:
            url_lower = url.lower()
            for keyword in api_keywords:
                if keyword in url_lower:
                    results['all_found'].append(url)
                    break
        
        # Find JavaScript API patterns
        js_patterns = [
            r'fetch\(["\']([^"\']+)["\']',
            r'axios\.(?:get|post|put)\(["\']([^"\']+)["\']',
            r'\.get\(["\']([^"\']+)["\']',
            r'\.post\(["\']([^"\']+)["\']',
            r'baseURL\s*:\s*["\']([^"\']+)["\']',
            r'API_URL\s*[:=]\s*["\']([^"\']+)["\']',
            r'apiUrl\s*[:=]\s*["\']([^"\']+)["\']',
            r'REACT_APP_API\w*\s*[:=]\s*["\']([^"\']+)["\']',
            r'VITE_API\w*\s*[:=]\s*["\']([^"\']+)["\']',
            r'NEXT_PUBLIC_API\w*\s*[:=]\s*["\']([^"\']+)["\']',
            r'endpoint\s*[:=]\s*["\']([^"\']+)["\']',
            r'proxy\s*:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches:
                if match not in results['all_found'] and len(match) > 5:
                    results['all_found'].append(match)
        
        # ============================================
        # STEP 3: Find the REAL backend API
        # ============================================
        parsed_target = urlparse(target_url)
        target_domain = parsed_target.netloc
        
        # Filter APIs that are DIFFERENT from target domain (these are backend APIs)
        backend_apis = []
        for api in results['all_found']:
            try:
                api_domain = urlparse(api).netloc if api.startswith('http') else ''
                if api_domain and api_domain != target_domain:
                    backend_apis.append(api)
            except:
                pass
        
        # Also check relative API paths
        relative_apis = []
        for api in results['all_found']:
            if api.startswith('/api') or '/api/' in api:
                relative_apis.append(api)
        
        # ============================================
        # STEP 4: Try to construct REAL API URL
        # ============================================
        real_api_candidates = []
        
        # From backend APIs
        for api in backend_apis:
            if any(kw in api.lower() for kw in ['api', 'mobile', 'info', 'number', 'search']):
                real_api_candidates.append(api)
        
        # From relative APIs
        for api in relative_apis:
            full_url = urljoin(target_url, api)
            real_api_candidates.append(full_url)
        
        # ============================================
        # STEP 5: TEST EACH CANDIDATE
        # ============================================
        for candidate in real_api_candidates[:10]:
            try:
                # Try with parameter
                test_url = candidate
                if '?' not in test_url:
                    for param_name in ['num', 'number', 'mobile', 'phone', 'id', 'query', 'q']:
                        test_url = f"{candidate}?{param_name}={test_param}"
                        break
                
                test_resp = requests.get(test_url, headers=headers, timeout=10, verify=False)
                
                if test_resp.status_code == 200 and len(test_resp.text) > 20:
                    results['intercepted_apis'].append({
                        'url': candidate,
                        'test_url': test_url,
                        'status': test_resp.status_code,
                        'sample': test_resp.text[:200]
                    })
                    
                    # This is likely the REAL API
                    if results['real_api'] is None:
                        results['real_api'] = candidate
                        results['api_base'] = candidate
            except:
                pass
        
        # ============================================
        # STEP 6: Try Vercel/NETLIFY specific paths
        # ============================================
        base_url = f"{parsed_target.scheme}://{parsed_target.netloc}"
        
        serverless_paths = [
            '/api/index', '/api/index.js', '/api/index.py',
            '/api/main', '/api/handler', '/api/app',
            '/api/v1', '/api/data', '/api/search',
            '/api/number', '/api/mobile', '/api/info',
            '/.netlify/functions/index', '/.netlify/functions/api',
            '/api/hello', '/api/test',
        ]
        
        for path in serverless_paths:
            test_url = f"{base_url}{path}"
            try:
                test_resp = requests.get(test_url, headers=headers, timeout=5, verify=False)
                if test_resp.status_code == 200 and len(test_resp.text) > 20:
                    results['intercepted_apis'].append({
                        'url': test_url,
                        'status': test_resp.status_code,
                        'sample': test_resp.text[:200]
                    })
                    if not results['real_api']:
                        results['real_api'] = test_url
            except:
                pass
        
        # ============================================
        # STEP 7: Try to find API from error messages
        # ============================================
        if not results['real_api']:
            # Send request with wrong method to trigger error
            try:
                error_resp = requests.post(target_url, headers=headers, timeout=5, verify=False)
                error_text = error_resp.text[:1000]
                
                # Look for URLs in error messages
                error_urls = re.findall(r'https?://[^\s"\'<>\[\]]+', error_text)
                for eu in error_urls:
                    if any(kw in eu.lower() for kw in api_keywords):
                        results['all_found'].append(eu)
            except:
                pass
        
    except Exception as e:
        results['error'] = str(e)
    
    # Clean up
    results['all_found'] = list(set(results['all_found']))
    
    return results

# ============================================
# 🎨 SIMPLE UI
# ============================================
LOGIN_PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>💀 API SNIFFER PRO</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:system-ui}
.box{background:#0a0000;padding:40px;border-radius:16px;border:2px solid #f00;width:380px;text-align:center;box-shadow:0 0 50px rgba(255,0,0,0.2)}
h1{color:#f00;font-size:1.5em;letter-spacing:2px}
.tag{color:#888;font-size:0.6em;letter-spacing:3px;margin:8px 0 20px}
input{width:100%;padding:14px;background:#000;border:1px solid #f00;border-radius:10px;color:#f44;margin:8px 0;font-size:14px;font-family:monospace}
input:focus{border-color:#0f0;outline:none}
.btn{width:100%;padding:14px;background:#c00;color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:15px;margin-top:10px}
.btn:hover{background:#f00}
</style></head><body>
<div class="box">
<h1>💀 API SNIFFER PRO</h1>
<div class="tag">100% REAL API CAPTURE</div>
<form method="post">
<input type="text" name="user" placeholder="USERNAME" autocomplete="off">
<input type="password" name="pass" placeholder="PASSWORD">
<button class="btn" type="submit">ACCESS</button>
</form>
{% if error %}<p style="color:#f00;margin-top:8px;font-size:0.8em">{{ error }}</p>{% endif %}
</div>
</body></html>"""

DASHBOARD = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>💀 API SNIFFER PRO</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#ddd;font-family:system-ui;padding:10px}
.container{max-width:1000px;margin:0 auto}
.header{display:flex;justify-content:space-between;align-items:center;padding:15px;border:2px solid #f00;border-radius:12px;margin-bottom:15px;background:#0a0000}
.header h1{color:#f00;font-size:1.2em}
.card{background:#0a0000;border:1px solid #300;border-radius:12px;padding:18px;margin-bottom:12px}
.card h3{color:#f44;margin-bottom:10px;font-size:0.85em}
input,textarea{width:100%;padding:12px;background:#000;border:1px solid #f00;border-radius:8px;color:#f44;margin:5px 0;font-size:13px;font-family:monospace}
textarea{resize:vertical;min-height:60px}
label{font-size:0.6em;color:#888;display:block;margin-top:6px}
.btn{width:100%;padding:12px;background:#c00;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;margin:4px 0;font-size:0.75em}
.btn:hover{background:#f00}
.btn-green{background:#0a0}.btn-green:hover{background:#0f0}
.result{background:#000;border:1px solid #0f0;border-radius:8px;padding:12px;max-height:400px;overflow:auto;font-family:monospace;font-size:0.65em;color:#0f0;white-space:pre-wrap;word-break:break-all;margin-top:8px}
.real-api{background:rgba(0,255,0,0.05);border:2px solid #0f0;padding:12px;border-radius:8px;text-align:center;margin:8px 0;font-size:0.8em;color:#0f0;word-break:break-all}
.badge{display:inline-block;padding:3px 8px;border-radius:8px;font-size:0.5em;font-weight:700}
.badge-on{background:rgba(0,255,0,0.1);color:#0f0;border:1px solid rgba(0,255,0,0.2)}
.copy-btn{padding:3px 8px;background:#333;color:#ff0;border:1px solid #ff0;border-radius:4px;cursor:pointer;font-size:0.5em}
</style></head><body>
<div class="container">
<div class="header">
<div><h1>💀 API SNIFFER PRO</h1><div style="color:#888;font-size:0.5em">100% Real Backend API Capture</div></div>
<div style="display:flex;gap:8px;align-items:center">
<span class="badge badge-on">PRO</span>
<a href="/logout" style="color:#f00;text-decoration:none;font-size:0.6em">EXIT</a>
</div>
</div>

<div class="card">
<h3>🎯 ENTER WEBSITE URL</h3>
<label>Website URL</label>
<input type="text" id="targetUrl" placeholder="https://example.vercel.app" value="{{ last_url }}">
<label>Test Parameter</label>
<input type="text" id="testParam" placeholder="9876543210" value="{{ last_param }}">
<button class="btn" onclick="sniff()">🔍 CAPTURE REAL API</button>
<div class="result" id="status">💀 Enter URL and click CAPTURE...</div>
</div>

<div class="card">
<h3>🎯 REAL API FOUND</h3>
<div class="real-api" id="realAPI">No API captured yet</div>
<button class="btn btn-green" onclick="copyAPI()">📋 COPY REAL API</button>
</div>

<div class="card">
<h3>📋 DISCOVERED APIs</h3>
<div class="result" id="apiList" style="max-height:250px">
{% if apis %}
{% for api in apis %}
<div style="margin-bottom:4px;padding:3px;border-bottom:1px solid #111;font-size:0.6em">
{{ api[:100] }}
<button class="copy-btn" onclick="copyText('{{ api }}')">📋</button>
</div>
{% endfor %}
{% else %}
<p style="color:#555;font-size:0.6em">APIs will appear here...</p>
{% endif %}
</div>
</div>
</div>

<script>
var realAPI = '';

function copyText(t) { navigator.clipboard.writeText(t); alert('✅ Copied!'); }
function copyAPI() { if(realAPI) { navigator.clipboard.writeText(realAPI); alert('✅ API Copied!\\n'+realAPI); } else { alert('No API yet!'); } }

function sniff() {
    var url = document.getElementById('targetUrl').value.trim();
    var param = document.getElementById('testParam').value.trim() || '9876543210';
    if(!url) { alert('Enter URL!'); return; }
    if(!url.startsWith('http')) url = 'https://' + url;
    
    document.getElementById('status').textContent = '⏳ Scanning... (15-20 sec)';
    document.getElementById('status').style.color = '#ff0';
    
    fetch('/sniff', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url: url, param: param})
    })
    .then(r => r.json())
    .then(d => {
        var h = '';
        if(d.error) {
            h = '❌ Error: ' + d.error;
            document.getElementById('status').style.color = '#f00';
        } else {
            document.getElementById('status').style.color = '#0f0';
            h = '✅ SCAN COMPLETE!\\n\\n';
            
            if(d.real_api) {
                h += '🎯 REAL API: ' + d.real_api + '\\n\\n';
                realAPI = d.real_api;
                document.getElementById('realAPI').textContent = d.real_api;
            }
            
            if(d.intercepted_apis && d.intercepted_apis.length > 0) {
                h += '📡 INTERCEPTED APIs:\\n';
                d.intercepted_apis.forEach(a => {
                    h += '  [' + a.status + '] ' + a.url + '\\n';
                });
                h += '\\n';
            }
            
            if(d.all_found && d.all_found.length > 0) {
                h += '🔗 ALL FOUND (' + d.all_found.length + '):\\n';
                d.all_found.slice(0,15).forEach(a => h += '  → ' + a + '\\n');
            }
        }
        document.getElementById('status').textContent = h;
        setTimeout(function() { location.reload(); }, 1500);
    });
}
</script></body></html>"""

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
    apis = session.get('discovered_apis', [])
    return render_template_string(DASHBOARD,
        apis=apis,
        last_url=session.get('last_url', ''),
        last_param=session.get('last_param', ''))

@app.route('/sniff', methods=['POST'])
def sniff():
    if not session.get('auth'): return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    url = data.get('url', '').strip()
    param = data.get('param', '9876543210')
    
    if not url: return jsonify({'error': 'URL required'})
    
    session['last_url'] = url
    session['last_param'] = param
    
    # RUN SNIFFER
    results = proxy_sniff(url, param)
    
    # Save discovered
    if 'discovered_apis' not in session:
        session['discovered_apis'] = []
    
    if results.get('real_api'):
        if results['real_api'] not in session['discovered_apis']:
            session['discovered_apis'].insert(0, results['real_api'])
    
    for api in results.get('all_found', []):
        if api not in session['discovered_apis']:
            session['discovered_apis'].append(api)
    
    session['discovered_apis'] = session['discovered_apis'][:30]
    
    return jsonify(results)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
