import re

landing_path = "internship_ai_agent/landing.html"
with open(landing_path, "r") as f:
    landing_html = f.read()

# Remove the Three.js initialization and event listener
landing_html = re.sub(r"// --- Three\.js Implementation ---.*?window\.addEventListener\('load', initThreeJS\);", "", landing_html, flags=re.DOTALL)

# Remove the canvas container div
landing_html = re.sub(r"<!-- 3D Model Canvas -->\s*<div id=\"canvas-container\"></div>", "", landing_html)

# Remove the canvas container css
landing_html = re.sub(r"/\* 3D Canvas Container \*/.*?pointer-events: none;\s*}", "", landing_html, flags=re.DOTALL)

with open(landing_path, "w") as f:
    f.write(landing_html)

for dashboard_path in ["internship_ai_agent/index.html", "internship_ai_agent/user-dashboard.html"]:
    with open(dashboard_path, "r") as f:
        dash_html = f.read()
    
    # Add onclick to startScanBtn if not present
    if 'id="startScanBtn"' in dash_html and "onclick" not in dash_html.split('id="startScanBtn"')[1].split('>')[0]:
        dash_html = dash_html.replace('id="startScanBtn" class=', 'id="startScanBtn" onclick="window.location.href=\'/bot\'" class=')
    
    with open(dashboard_path, "w") as f:
        f.write(dash_html)

print("Fixes applied successfully.")
