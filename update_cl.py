import os
import re

# Use relative paths from the script's directory
base_dir = os.path.dirname(os.path.abspath(__file__))
files_to_update = [
    os.path.join(base_dir, "internship_ai_agent", "index.html"),
    os.path.join(base_dir, "internship_ai_agent", "user-dashboard.html")
]

replacement_content = """            <div class="space-y-4 mb-6">
                <!-- Resume upload removed; using saved resume from server -->
                <div>
                    <label class="block text-xs text-gray-400 mb-1">Target Job Title</label>
                    <input type="text" id="clJobTitle" placeholder="e.g. Frontend Developer" class="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-[#00f0ff] transition-colors">
                </div>
                <div>
                    <label class="block text-xs text-gray-400 mb-1">Company</label>
                    <input type="text" id="clCompany" placeholder="e.g. Google" class="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-[#00f0ff] transition-colors">
                </div>
            </div>
            
            <button id="submitGenerateCL" class="w-full skeu-btn-primary py-3 rounded-xl font-bold text-lg">Generate Now</button>
            <div id="clError" class="hidden text-red-400 text-sm mt-3 text-center bg-red-500/10 py-2 rounded-lg border border-red-500/20"></div>
            
            <div id="clResult" class="hidden mt-6">
                <textarea id="clEditor" class="w-full h-48 bg-black/50 border border-white/10 rounded-xl p-4 text-xs font-mono text-gray-300 outline-none mb-4"></textarea>
                <div class="flex gap-3">
                    <button id="clDownloadPdf" class="flex-1 py-2 rounded-lg bg-red-500/20 border border-red-500/40 text-red-400 font-bold hover:bg-red-500/30">Download PDF</button>
                    <button id="clDownloadDocx" class="flex-1 py-2 rounded-lg bg-blue-500/20 border border-blue-500/40 text-blue-400 font-bold hover:bg-blue-500/30">Download DOCX</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Animations
        gsap.from(".glass-panel", { y: 30, opacity: 0, duration: 0.8, stagger: 0.1, ease: "power3.out" });
        
        // Modal Logic
        const modal = document.getElementById('coverLetterModal');
        document.getElementById('openCoverLetterModalBtn').onclick = () => { modal.style.display = 'flex'; gsap.from(modal.children[0], {scale:0.9, opacity:0, duration:0.3, ease:"back.out"}); }
        document.getElementById('closeCoverLetterModal').onclick = () => modal.style.display = 'none';
        
        // Cover Letter Logic
        document.getElementById('submitGenerateCL').onclick = async () => {
            const btn = document.getElementById('submitGenerateCL');
            const errorDiv = document.getElementById('clError');
            const resultDiv = document.getElementById('clResult');
            const editor = document.getElementById('clEditor');
            const jobTitle = document.getElementById('clJobTitle').value;
            const company = document.getElementById('clCompany').value;
            
            errorDiv.classList.add('hidden');
            resultDiv.style.display = 'none';
            
            btn.innerHTML = `<span class="animate-spin w-5 h-5 border-2 border-black/20 border-t-black rounded-full inline-block"></span> Generating...`;
            btn.disabled = true;

            const formData = new FormData();
            formData.append('jobTitle', jobTitle);
            formData.append('company', company);

            try {
                const token = localStorage.getItem('token') || '';
                const res = await fetch('/api/generate-cover-letter', {
                    method: 'POST',
                    headers: { 'Authorization': 'Bearer ' + token },
                    body: formData
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    editor.value = data.cover_letter;
                    resultDiv.style.display = 'block';
                    btn.innerHTML = 'Regenerate';
                } else {
                    throw new Error(data.error || 'Failed to generate cover letter.');
                }
            } catch(err) {
                errorDiv.innerText = err.message;
                errorDiv.classList.remove('hidden');
                btn.innerHTML = 'Generate Now';
            } finally {
                btn.disabled = false;
            }
        };

        const downloadCL = async (format) => {
            const text = document.getElementById('clEditor').value;
            if(!text) return;
            
            try {
                const res = await fetch('/api/download-cover-letter', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, format })
                });
                
                if (res.ok) {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `Cover_Letter_${document.getElementById('clCompany').value || 'Company'}.${format}`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                } else {
                    alert("Failed to download cover letter.");
                }
            } catch(err) {
                alert("Error downloading cover letter.");
            }
        };

        document.getElementById('clDownloadPdf').onclick = () => downloadCL('pdf');
        document.getElementById('clDownloadDocx').onclick = () => downloadCL('docx');
    </script>
"""

regex_pattern = re.compile(
    r'<div class="space-y-4 mb-6">.*?<script>.*?</script>',
    re.DOTALL
)

for file_path in files_to_update:
    if not os.path.exists(file_path):
        print(f"Skipping {file_path} - not found.")
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace the chunk
    new_content = regex_pattern.sub(replacement_content, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {file_path} successfully.")

print("Cover letter logic updated successfully in dashboard pages.")
