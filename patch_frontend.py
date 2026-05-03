import os
from bs4 import BeautifulSoup
import re

base_dir = "/home/pritam-mondal/Desktop/new project/internship_ai_agent"

# Files to patch with just Tailwind and glassmorphism backgrounds (the ones we didn't fully rewrite)
files_to_patch = [
    "mock-interview.html",
    "contact-us.html",
    "terms-and-conditions.html",
    "privacy-policy.html"
]

tailwind_script = '<script src="https://cdn.tailwindcss.com"></script>\n'
config_script = """<script>
    tailwind.config = {
        theme: {
            extend: {
                fontFamily: { sans: ['Inter', 'sans-serif'], display: ['Outfit', 'sans-serif'] },
                colors: { brandPrimary: '#00f0ff', brandSecondary: '#7000ff' }
            }
        }
    }
</script>"""

gsap_scripts = """<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>"""

new_style = """
<style>
    body { background: #030305; color: #fff; overflow-x: hidden; }
    .glass-panel {
        background: rgba(20, 20, 25, 0.4); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08); border-top: 1px solid rgba(255, 255, 255, 0.15); border-left: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .liquid-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -2; overflow: hidden; pointer-events: none;}
    .blob { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.3; animation: float 20s infinite alternate ease-in-out; }
    .blob-1 { width: 40vw; height: 40vw; background: #00f0ff; top: 10%; right: -10%; }
    .blob-2 { width: 50vw; height: 50vw; background: #7000ff; bottom: -10%; left: -10%; animation-delay: -5s; }
    @keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(-5vw, 10vh) scale(1.1); } }
</style>
"""

liquid_bg_html = """
<div class="liquid-bg">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
</div>
<video class="fixed inset-0 w-full h-full object-cover opacity-10 mix-blend-screen z-[-1]" autoplay loop muted playsinline>
    <source src="/images/6325848-hd_1920_1080_25fps.mp4" type="video/mp4">
</video>
"""

for filename in files_to_patch:
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Use regex to inject if we can't easily parse
    if "<head>" in html_content and "tailwindcss.com" not in html_content:
        html_content = html_content.replace("<head>", f"<head>\n{tailwind_script}\n{config_script}\n{gsap_scripts}\n{new_style}")
    
    if "<body>" in html_content and "liquid-bg" not in html_content:
        html_content = html_content.replace("<body>", f"<body>\n{liquid_bg_html}")
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

print("Patching complete.")
