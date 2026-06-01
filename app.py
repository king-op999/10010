from flask import Flask, request, jsonify, render_template_string, session, redirect
import requests
import re
import json
from urllib.parse import urlparse, urljoin
import ssl
import socket

app = Flask(__name__)
app.secret_key = 'bronx_ultra_sniffer_v2_2024'

ADMIN_USER = "bronx"
ADMIN_PASS = "ultra2026"

# ============================================
# 💀 UNIVERSAL API SNIFFER ENGINE
# ============================================
def universal_sniff(target_url, test_param="9876543210"):
    """
    UNIVERSAL API SNIFFER - Finds real backend API from ANY hosted site
    Works with: Vercel, Netlify, Render, Railway, Heroku, GitHub Pages, etc.
    """
    results = {
        'original_url': target_url,
        'real_api_found': None,
        'all_discovered_apis': [],
        'backend_urls': [],
        'env_variables': [],
        'js_files_scanned': [],
        'api_endpoints_tested': []
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    parsed = urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    domain = parsed.netloc.replace('.vercel.app', '').replace('.netlify.app', '').replace('.onrender.com', '').replace('.railway.app', '')
    
    try:
        # ============================================
        # STEP 1: GET MAIN PAGE + FIND JS FILES
        # ============================================
        print(f"🔍 [1/6] Scanning: {target_url}")
        resp = requests.get(target_url, headers=headers, timeout=15, allow_redirects=True)
        page_source = resp.text
        html_headers = dict(resp.headers)
        
        # Find ALL JavaScript files
        js_files = []
        
        # <script src="...">
        script_matches = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', page_source)
        js_files.extend(script_matches)
        
        # import ... from "..."
        import_matches = re.findall(r'import\s+.*?from\s+["\']([^"\']+)["\']', page_source)
        js_files.extend(import_matches)
        
        # require("...")
        require_matches = re.findall(r'require\(["\']([^"\']+)["\']\)', page_source)
        js_files.extend(require_matches)
        
        # _next/static chunks (Next.js)
        next_matches = re.findall(r'["\'](/[_]next/[^"\']+)["\']', page_source)
        js_files.extend(next_matches)
        
        # Make absolute URLs
        for i, js in enumerate(js_files):
            if js.startswith('//'):
                js_files[i] = f"https:{js}"
            elif js.startswith('/'):
                js_files[i] = urljoin(base_url, js)
            elif not js.startswith('http'):
                js_files[i] = urljoin(base_url, js)
        
        # Deduplicate
        js_files = list(set(js_files))
        results['js_files_scanned'] = js_files[:10]
        
        # ============================================
        # STEP 2: SCAN EACH JS FILE FOR API PATTERNS
        # ============================================
        print(f"🔍 [2/6] Scanning {len(js_files)} JS files...")
        
        api_patterns = []
        
        for js_url in js_files[:15]:  # Scan first 15 JS files
            try:
                js_resp = requests.get(js_url, headers=headers, timeout=10)
                js_content = js_resp.text
                
                # Pattern 1: Full URLs with API-like paths
                url_matches = re.findall(r'["\'\`](https?://[^"\'\`\s]+(?:api|mobile|info|search|lookup|data|get|fetch|query|backend|server|endpoint)[^"\'\`\s]*)["\'\`]', js_content, re.IGNORECASE)
                api_patterns.extend(url_matches)
                
                # Pattern 2: Variable assignments
                var_matches = re.findall(r'(?:const|let|var)\s+\w*(?:API|api|BASE|base|URL|url|ENDPOINT|endpoint|BACKEND|backend|SERVER|server)\w*\s*[=:]\s*["\'\`]([^"\'\`]+)["\'\`]', js_content)
                api_patterns.extend(var_matches)
                
                # Pattern 3: fetch/axios calls
                fetch_matches = re.findall(r'fetch\(["\'\`]([^"\'\`]+)["\'\`]\)', js_content)
                api_patterns.extend(fetch_matches)
                
                axios_matches = re.findall(r'axios\.(?:get|post|put|delete)\(["\'\`]([^"\'\`]+)["\'\`]\)', js_content)
                api_patterns.extend(axios_matches)
                
                # Pattern 4: Proxy configurations
                proxy_matches = re.findall(r'["\'\`]proxy["\'\`]\s*:\s*["\'\`]([^"\'\`]+)["\'\`]', js_content)
                api_patterns.extend(proxy_matches)
                
                # Pattern 5: Rewrites/redirects
                rewrite_matches = re.findall(r'["\'\`]destination["\'\`]\s*:\s*["\'\`]([^"\'\`]+)["\'\`]', js_content)
                api_patterns.extend(rewrite_matches)
                
            except:
                continue
        
        # ============================================
        # STEP 3: SCAN HTML FOR API HINTS
        # ============================================
        print(f"🔍 [3/6] Scanning HTML...")
        
        # Meta tags
        meta_matches = re.findall(r'<meta[^>]+content=["\']([^"\']*(?:api|endpoint|url)[^"\']*)["\']', page_source, re.IGNORECASE)
        api_patterns.extend(meta_matches)
        
        # Data attributes
        data_matches = re.findall(r'data-(?:api|url|endpoint|backend)=["\']([^"\']+)["\']', page_source)
        api_patterns.extend(data_matches)
        
        # Inline scripts
        inline_matches = re.findall(r'(?:apiUrl|API_URL|baseUrl|BASE_URL|endpoint|backendUrl)\s*[=:]\s*["\'\`]([^"\'\`]+)["\'\`]', page_source)
        api_patterns.extend(inline_matches)
        
        # ============================================
        # STEP 4: TRY COMMON API PATHS
        # ============================================
        print(f"🔍 [4/6] Testing common API paths...")
        
        common_paths = [
            '/api', '/api/v1', '/api/v2',
            '/api/mobile', '/api/number', '/api/info',
            '/api/search', '/api/lookup', '/api/data',
            '/api/check', '/api/get', '/api/query',
            '/mobile', '/info', '/search', '/lookup',
            '/.netlify/functions/api',
            '/api/index', '/api/index.js',
            '/api/index.py', '/api/main',
        ]
        
        for path in common_paths:
            test_url = urljoin(base_url, path)
            try:
                test_resp = requests.get(test_url, headers=headers, timeout=5)
                if test_resp.status_code != 404:
                    results['api_endpoints_tested'].append({
                        'url': test_url,
                        'status': test_resp.status_code,
                        'type': test_resp.headers.get('content-type', '?'),
                        'sample': test_resp.text[:150]
                    })
            except:
                pass
        
        # ============================================
        # STEP 5: ENVIRONMENT DISCOVERY
        # ============================================
        print(f"🔍 [5/6] Probing environment...")
        
        env_paths = [
            '/.env', '/.env.local', '/.env.production',
            '/env.json', '/config.json', '/settings.json',
            '/package.json', '/vercel.json', '/netlify.toml',
            '/_next/static/chunks/pages/_app.js',
            '/build-manifest.json',
        ]
        
        for env_path in env_paths:
            test_url = urljoin(base_url, env_path)
            try:
                test_resp = requests.get(test_url, headers=headers, timeout=5)
                if test_resp.status_code == 200 and len(test_resp.text) > 10:
                    env_content = test_resp.text[:1000]
                    
                    # Find API URLs in config files
                    config_urls = re.findall(r'["\'](https?://[^"\']+(?:api|mobile|backend|server)[^"\']*)["\']', env_content, re.IGNORECASE)
                    api_patterns.extend(config_urls)
                    
                    results['env_variables'].append({
                        'file': env_path,
                        'found_urls': config_urls
                    })
            except:
                pass
        
        # ============================================
        # STEP 6: DEDUPLICATE & FIND REAL API
        # ============================================
        print(f"🔍 [6/6] Analyzing results...")
        
        # Clean and deduplicate
        clean_apis = []
        for api in api_patterns:
            api = api.strip().strip('"').strip("'").strip('`')
            if api and len(api) > 10 and 'http' in api.lower():
                # Remove localhost
                if 'localhost' not in api and '127.0.0.1' not in api:
                    clean_apis.append(api)
        
        clean_apis = list(set(clean_apis))
        results['all_discovered_apis'] = clean_apis
        
        # FIND THE MOST LIKELY REAL API
        real_api = None
        
        # Priority 1: Direct API URLs with parameters
        for api in clean_apis:
            if re.search(r'(?:api|mobile|info|search|lookup|data|get|fetch|query|backend|server|endpoint)', api, re.IGNORECASE):
                if '?' in api or re.search(r'[=:]\d+', api):
                    real_api = api
                    break
        
        # Priority 2: Clean API base URLs
        if not real_api:
            for api in clean_apis:
                if '/api/' in api or '/mobile/' in api or '/info/' in api:
                    real_api = api
                    break
        
        # Priority 3: Any URL that's not the original site
        if not real_api and clean_apis:
            for api in clean_apis:
                if parsed.netloc not in api:
                    real_api = api
                    break
        
        # Priority 4: First available
        if not real_api and clean_apis:
            real_api = clean_apis[0]
        
        # Try to build complete API URL with parameter
        if real_api:
            if '?' not in real_api and '=' not in real_api:
                if real_api.endswith('/'):
                    real_api = real_api[:-1]
                # Common parameter patterns
                for param_name in ['num', 'number', 'mobile', 'phone', 'id', 'query', 'q', 'search', 'data']:
                    test_full_url = f"{real_api}?{param_name}={test_param}"
                    try:
                        test_resp = requests.get(test_full_url, headers=headers, timeout=5)
                        if test_resp.status_code == 200 and len(test_resp.text) > 50:
                            real_api = test_full_url
                            break
                    except:
                        continue
        
        results['real_api_found'] = real_api
        
        print(f"✅ REAL API FOUND: {real_api}")
        
    except Exception as e:
        results['error'] = str(e)
        print(f"❌ Error: {e}")
    
    return results

# ============================================
# 🎨 UI
# ============================================
LOGIN_PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>💀 BRONX UNIVERSAL SNIFFER</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:system-ui}
.bg{position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(circle,rgba(255,0,0,0.03) 1px,transparent 1px);background-size:30px 30px;animation:bg 15s linear infinite}
@keyframes bg{0%{transform:translate(0)}100%{transform:translate(30px,30px)}}
.box{background:rgba(10,0,0,0.95);padding:45px;border-radius:18px;border:2px solid #f00;width:400px;text-align:center;z-index:1;box-shadow:0 0 60px rgba(255,0,0,0.3);position:relative}
h1{color:#f00;font-size:1.5em;letter-spacing:2px;margin-bottom:5px}
.tag{color:#888;font-size:0.6em;letter-spacing:3px;margin:8px 0 20px}
input{width:100%;padding:14px;background:#000;border:1px solid #f00;border-radius:10px;color:#f44;margin:8px 0;font-size:14px;font-family:monospace}
input:focus{border-color:#0f0;outline:none}
.btn{width:100%;padding:14px;background:#c00;color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:15px;margin-top:10px;letter-spacing:2px}
.btn:hover{background:#f00}
.msg{color:#f00;margin-top:10px;font-size:0.8em}
</style></head><body>
<div class="bg"></div>
<div class="box">
<h1>💀 API SNIFFER</h1>
<div class="tag">UNIVERSAL BACKEND CAPTURE</div>
<p style="color:#888;font-size:0.55em">Works: Vercel | Netlify | Render | Railway | All</p>
<form method="post">
<input type="text" name="user" placeholder="🔑 USERNAME" autocomplete="off">
<input type="password" name="pass" placeholder="🔐 PASSWORD">
<button class="btn" type="submit">☠️ ACCESS TOOL</button>
</form>
{% if error %}<p class="msg">{{ error }}</p>{% endif %}
</div>
</body></html>"""

DASHBOARD = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>💀 API SNIFFER v2.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#e0e0e0;font-family:system-ui;padding:12px}
.container{max-width:1200px;margin:0 auto}
.header{display:flex;justify-content:space-between;align-items:center;padding:15px 20px;border:2px solid #f00;border-radius:12px;margin-bottom:15px;background:#0a0000;flex-wrap:wrap;gap:10px}
.header h1{color:#f00;font-size:1.3em;letter-spacing:2px}
.card{background:#0a0000;border:1px solid #300;border-radius:12px;padding:20px;margin-bottom:15px}
.card h3{color:#f44;margin-bottom:12px;font-size:0.9em}
input,textarea{width:100%;padding:12px;background:#000;border:1px solid #f00;border-radius:8px;color:#f44;margin:5px 0;font-size:13px;font-family:monospace}
textarea{resize:vertical;min-height:60px}
label{font-size:0.6em;color:#888;text-transform:uppercase;letter-spacing:1px;display:block;margin-top:6px}
.btn{width:100%;padding:14px;background:#c00;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;margin:5px 0;font-size:0.8em;letter-spacing:1px}
.btn:hover{background:#f00}
.btn-green{background:#0a0}.btn-green:hover{background:#0f0}
.result-box{background:#000;border:1px solid #0f0;border-radius:8px;padding:15px;max-height:500px;overflow:auto;font-family:monospace;font-size:0.7em;color:#0f0;white-space:pre-wrap;word-break:break-all;margin-top:8px}
.copy-btn{padding:3px 8px;background:#333;color:#ff0;border:1px solid #ff0;border-radius:4px;cursor:pointer;font-size:0.55em}
.real-api-highlight{background:rgba(255,0,0,0.1);border:2px solid #0f0;padding:10px;border-radius:8px;margin:8px 0;font-size:0.8em;color:#0f0;text-align:center}
.badge{display:inline-block;padding:4px 10px;border-radius:10px;font-size:0.5em;font-weight:700}
.badge-on{background:rgba(0,255,0,0.1);color:#0f0;border:1px solid rgba(0,255,0,0.3)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:768px){.grid2{grid-template-columns:1fr}}
</style></head><body>
<div class="container">
<div class="header">
<div><h1>💀 UNIVERSAL API SNIFFER v2.0</h1><div style="color:#888;font-size:0.5em">100% Real Backend API Capture | Vercel/Netlify/Render/Railway</div></div>
<div style="display:flex;gap:8px;align-items:center">
<span class="badge badge-on">✅ READY</span>
<a href="/logout" style="color:#f00;text-decoration:none;font-size:0.65em">EXIT</a>
</div>
</div>

<div class="card">
<h3>🎯 ENTER WEBSITE URL</h3>
<label>Website URL (Any hosted site)</label>
<input type="text" id="targetUrl" placeholder="https://example.vercel.app" value="{{ last_url }}">
<label>Test Parameter</label>
<input type="text" id="testParam" placeholder="9876543210" value="{{ last_param }}">
<button class="btn" onclick="sniffAPI()">🔍 CAPTURE REAL API</button>
<div class="result-box" id="status">💀 Ready. Enter URL and click CAPTURE...</div>
</div>

<div class="grid2">
<div class="card">
<h3>🎯 REAL API FOUND</h3>
<div class="real-api-highlight" id="realAPI">No API found yet</div>
<button class="btn btn-green" onclick="copyRealAPI()">📋 COPY REAL API</button>
</div>

<div class="card">
<h3>📋 ALL DISCOVERED APIs</h3>
<div class="result-box" id="apiList" style="max-height:300px">
{% if apis %}
{% for api in apis %}
<div style="margin-bottom:6px;padding:4px;border-bottom:1px solid #111">
<span style="color:#ff0;font-size:0.6em">{{ api[:80] }}</span>
<button class="copy-btn" onclick="copyText('{{ api }}')">📋</button>
</div>
{% endfor %}
{% else %}
<p style="color:#555;font-size:0.6em">APIs will appear here after scanning...</p>
{% endif %}
</div>
</div>
</div>
</div>

<script>
var currentRealAPI = '';

function copyText(text) {
    navigator.clipboard.writeText(text);
    alert('✅ Copied!');
}

function copyRealAPI() {
    if (currentRealAPI) {
        navigator.clipboard.writeText(currentRealAPI);
        alert('✅ REAL API COPIED!\\n' + currentRealAPI);
    } else {
        alert('⚠ No API found yet!');
    }
}

function sniffAPI() {
    var url = document.getElementById('targetUrl').value.trim();
    var param = document.getElementById('testParam').value.trim() || '9876543210';
    
    if (!url) {
        alert('Enter URL!');
        return;
    }
    
    if (!url.startsWith('http')) {
        url = 'https://' + url;
    }
    
    document.getElementById('status').textContent = '⏳ Scanning... (This may take 10-20 seconds)';
    document.getElementById('status').style.color = '#ff0';
    
    fetch('/sniff', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url: url, param: param})
    })
    .then(r => r.json())
    .then(d => {
        var html = '';
        
        if (d.error) {
            html = '❌ ERROR: ' + d.error;
            document.getElementById('status').style.color = '#f00';
        } else {
            document.getElementById('status').style.color = '#0f0';
            html += '✅ SCAN COMPLETE!\\n\\n';
            html += '📌 URL: ' + d.original_url + '\\n\\n';
            
            if (d.real_api_found) {
                html += '🎯 REAL API FOUND! ⬇\\n';
                html += '━'.repeat(50) + '\\n';
                html += d.real_api_found + '\\n';
                html += '━'.repeat(50) + '\\n\\n';
                currentRealAPI = d.real_api_found;
                document.getElementById('realAPI').textContent = d.real_api_found;
                document.getElementById('realAPI').style.color = '#0f0';
            } else {
                html += '⚠ No real API found in scan.\\n\\n';
            }
            
            if (d.all_discovered_apis && d.all_discovered_apis.length > 0) {
                html += '🔗 ALL DISCOVERED APIs (' + d.all_discovered_apis.length + '):\\n';
                d.all_discovered_apis.forEach(function(api) {
                    html += '  → ' + api.substring(0, 100) + '\\n';
                });
                html += '\\n';
            }
            
            if (d.js_files_scanned && d.js_files_scanned.length > 0) {
                html += '📁 JS Files Scanned: ' + d.js_files_scanned.length + '\\n';
                html += '\\n';
            }
        }
        
        document.getElementById('status').textContent = html;
        
        // Reload to update API list
        setTimeout(function() {
            location.reload();
        }, 1500);
    })
    .catch(function(e) {
        document.getElementById('status').textContent = '❌ Connection Error: ' + e.message;
        document.getElementById('status').style.color = '#f00';
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
        return render_template_string(LOGIN_PAGE, error="⛔ ACCESS DENIED")
    return render_template_string(LOGIN_PAGE, error=None)

@app.route('/dashboard')
def dashboard():
    if not session.get('auth'):
        return redirect('/')
    
    apis = session.get('discovered_apis', [])
    return render_template_string(DASHBOARD,
        apis=apis,
        last_url=session.get('last_url', ''),
        last_param=session.get('last_param', ''))

@app.route('/sniff', methods=['POST'])
def sniff():
    if not session.get('auth'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    url = data.get('url', '').strip()
    param = data.get('param', '9876543210')
    
    if not url:
        return jsonify({'error': 'URL required'})
    
    # Save for later
    session['last_url'] = url
    session['last_param'] = param
    
    # Run UNIVERSAL sniffer
    results = universal_sniff(url, param)
    
    # Save discovered APIs
    if 'discovered_apis' not in session:
        session['discovered_apis'] = []
    
    if results.get('real_api_found'):
        if results['real_api_found'] not in session['discovered_apis']:
            session['discovered_apis'].insert(0, results['real_api_found'])
    
    for api in results.get('all_discovered_apis', []):
        if api not in session['discovered_apis']:
            session['discovered_apis'].insert(0, api)
    
    session['discovered_apis'] = session['discovered_apis'][:30]
    
    return jsonify(results)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    print("💀 UNIVERSAL API SNIFFER v2.0")
    print("🔍 Works with: Vercel, Netlify, Render, Railway, Heroku, all!")
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
