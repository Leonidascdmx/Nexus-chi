import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from orchestrator.main_orchestrator import NexusOrchestrator

app = FastAPI(
    title="HI-NEXUS Agent API",
    description="FastAPI gateway for the HI-NEXUS multi-agent system",
    version="1.0.0"
)

# Initialize the central orchestrator
orchestrator = NexusOrchestrator()

class OrchestrateRequest(BaseModel):
    task: str

@app.get("/api/status")
async def get_status():
    """
    Returns system status, active agents, and environment variables configured.
    """
    return {
        "status": "online",
        "system": "HI-NEXUS",
        "agents": {
            "ResearchAgent": "Active",
            "BioAgent": "Active",
            "DevAgent": "Active"
        },
        "skills": [
            "web_search",
            "code_executor"
        ],
        "environment": {
            "GEMINI_API_KEY_CONFIGURED": os.environ.get("GEMINI_API_KEY") is not None,
            "OPENAI_API_KEY_CONFIGURED": os.environ.get("OPENAI_API_KEY") is not None,
            "TAVILY_API_KEY_CONFIGURED": os.environ.get("TAVILY_API_KEY") is not None,
            "SERPER_API_KEY_CONFIGURED": os.environ.get("SERPER_API_KEY") is not None
        }
    }

@app.post("/api/orchestrate")
async def orchestrate_task(request: OrchestrateRequest):
    """
    Triggers the orchestrator to route and resolve a task.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")
    
    result = orchestrator.execute_task(request.task)
    return result

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """
    Serves a stunning, premium, state-of-the-art interactive dashboard.
    """
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HI-NEXUS • Control Panel</title>
    <!-- Google Fonts Outfit & Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #080B11;
            --surface-color: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #F3F4F6;
            --text-secondary: #9CA3AF;
            --accent-primary: #6366F1; /* Indigo */
            --accent-secondary: #D946EF; /* Fuchsia */
            --accent-glow: rgba(99, 102, 241, 0.15);
            --success-color: #10B981;
            --warning-color: #F59E0B;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(217, 70, 239, 0.06) 0%, transparent 40%);
            background-attachment: fixed;
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow-x: hidden;
            line-height: 1.5;
        }

        header {
            width: 100%;
            max-width: 1200px;
            padding: 2.5rem 1.5rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-glow {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            box-shadow: 0 0 15px var(--accent-primary);
            animation: pulse 2s infinite alternate;
        }

        @keyframes pulse {
            0% { transform: scale(0.9); opacity: 0.8; box-shadow: 0 0 10px var(--accent-primary); }
            100% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 20px var(--accent-secondary); }
        }

        h1 {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 1.75rem;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #FFF, #A5B4FC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .status-pill {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: var(--success-color);
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: var(--success-color);
        }

        main {
            width: 100%;
            max-width: 1200px;
            padding: 0 1.5rem 3rem;
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
        }

        @media (min-width: 900px) {
            main {
                grid-template-columns: 380px 1fr;
            }
        }

        /* Glassmorphism Panel card styling */
        .glass-panel {
            background: var(--surface-color);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 1.25rem;
            padding: 2rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: all 0.3s ease;
        }

        .glass-panel:hover {
            border-color: rgba(255, 255, 255, 0.12);
        }

        .section-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1.25rem;
            color: #FFF;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .form-group {
            margin-bottom: 1.25rem;
        }

        label {
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            display: block;
        }

        textarea {
            width: 100%;
            height: 120px;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 1rem;
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            resize: none;
            outline: none;
            transition: border-color 0.25s, box-shadow 0.25s;
        }

        textarea:focus {
            border-color: var(--accent-primary);
            box-shadow: 0 0 10px var(--accent-glow);
        }

        .btn-orchestrate {
            width: 100%;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border: none;
            border-radius: 0.75rem;
            color: white;
            padding: 1rem;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-orchestrate:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }

        .btn-orchestrate:active {
            transform: translateY(0);
        }

        .agent-list {
            margin-top: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .agent-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 0.75rem;
            padding: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .agent-avatar {
            width: 40px;
            height: 40px;
            border-radius: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-family: 'Outfit', sans-serif;
            background: rgba(99, 102, 241, 0.1);
            color: var(--accent-primary);
        }

        .agent-card:nth-child(2) .agent-avatar {
            background: rgba(217, 70, 239, 0.1);
            color: var(--accent-secondary);
        }

        .agent-card:nth-child(3) .agent-avatar {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success-color);
        }

        .agent-info h4 {
            font-size: 0.9rem;
            font-weight: 600;
            color: #FFF;
        }

        .agent-info p {
            font-size: 0.75rem;
            color: var(--text-secondary);
        }

        /* Results Output Board */
        .output-container {
            display: flex;
            flex-direction: column;
            height: 100%;
            min-height: 500px;
        }

        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1rem;
            margin-bottom: 1.5rem;
        }

        .routed-tag {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 0.85rem;
            padding: 0.35rem 0.75rem;
            border-radius: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            display: none;
        }

        .output-body {
            flex-grow: 1;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 1.5rem;
            font-family: 'Inter', sans-serif;
            overflow-y: auto;
            max-height: 550px;
            white-space: pre-wrap;
        }

        .output-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--text-secondary);
            text-align: center;
            padding: 3rem 1rem;
        }

        .output-placeholder svg {
            width: 48px;
            height: 48px;
            stroke: rgba(255, 255, 255, 0.2);
            margin-bottom: 1rem;
        }

        /* Loader */
        .spinner {
            display: none;
            width: 24px;
            height: 24px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Markdown Rendering Simplification */
        .output-body h1, .output-body h2, .output-body h3 {
            font-family: 'Outfit', sans-serif;
            color: #FFF;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        .output-body h1 { font-size: 1.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 0.5rem; }
        .output-body h2 { font-size: 1.25rem; }
        .output-body h3 { font-size: 1.1rem; }
        .output-body p { margin-bottom: 1rem; color: #E5E7EB; font-size: 0.95rem; }
        .output-body ul, .output-body ol { margin-left: 1.5rem; margin-bottom: 1rem; }
        .output-body li { margin-bottom: 0.35rem; color: #E5E7EB; font-size: 0.95rem; }
        .output-body code {
            font-family: 'Courier New', Courier, monospace;
            background: rgba(255, 255, 255, 0.08);
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            font-size: 0.9rem;
            color: #F472B6;
        }
        .output-body pre {
            background: rgba(0, 0, 0, 0.5);
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-bottom: 1rem;
        }
        .output-body pre code {
            background: none;
            padding: 0;
            color: #A5B4FC;
            font-size: 0.85rem;
        }
        .output-body a {
            color: var(--accent-primary);
            text-decoration: none;
        }
        .output-body a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-container">
            <div class="logo-glow"></div>
            <h1>HI-NEXUS</h1>
        </div>
        <div class="status-pill">
            <div class="status-dot"></div>
            <span>Base System Active</span>
        </div>
    </header>

    <main>
        <!-- Left Column: Input and Agents -->
        <div class="glass-panel" style="display: flex; flex-direction: column; gap: 1.5rem;">
            <div>
                <h2 class="section-title">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    Orquestación de Tareas
                </h2>
                <div class="form-group">
                    <label for="task">Describe qué necesitas que haga HI-NEXUS:</label>
                    <textarea id="task" placeholder="Ej: Transcribir y traducir la secuencia de ADN ATGCGCGT... o 'Escribir una función que busque números primos'"></textarea>
                </div>
                <button class="btn-orchestrate" id="btnSubmit" onclick="runOrchestrator()">
                    <span id="btnText">Enviar a Nexus</span>
                    <div class="spinner" id="spinner"></div>
                </button>
            </div>

            <div>
                <h3 class="section-title">Agentes en el Nexus</h3>
                <div class="agent-list">
                    <div class="agent-card">
                        <div class="agent-avatar">R</div>
                        <div class="agent-info">
                            <h4>Research Agent</h4>
                            <p>Investigación web y síntesis factual</p>
                        </div>
                    </div>
                    <div class="agent-card">
                        <div class="agent-avatar">B</div>
                        <div class="agent-info">
                            <h4>Bioinformática Agent</h4>
                            <p>Análisis de secuencias y medicina molecular</p>
                        </div>
                    </div>
                    <div class="agent-card">
                        <div class="agent-avatar">D</div>
                        <div class="agent-info">
                            <h4>Software Dev Agent</h4>
                            <p>Ejecución y depuración de código Python</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Column: Live Output -->
        <div class="glass-panel output-container">
            <div class="output-header">
                <h2 class="section-title">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    Consola de Salida del Agente
                </h2>
                <span class="routed-tag" id="routedTag">Research-Agent</span>
            </div>
            <div class="output-body" id="outputBody">
                <div class="output-placeholder" id="placeholder">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p>Esperando instrucciones...</p>
                    <span style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">Escribe una consulta a la izquierda para activar los agentes.</span>
                </div>
            </div>
        </div>
    </main>

    <script>
        // Simple Markdown-to-HTML parser for local rendering
        function parseMarkdown(md) {
            let html = md;
            
            // Code blocks
            html = html.replace(/```python\n([\s\S]*?)\n```/g, '<pre><code class="language-python">$1</code></pre>');
            html = html.replace(/```text\n([\s\S]*?)\n```/g, '<pre><code class="language-text">$1</code></pre>');
            html = html.replace(/```([\s\S]*?)\n```/g, '<pre><code>$1</code></pre>');
            
            // Inline code
            html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
            
            // Headers
            html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
            html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
            html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
            
            // Bold
            html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
            
            // Bullet points
            html = html.replace(/^\- (.*?)$/gm, '<li>$1</li>');
            html = html.replace(/^\* (.*?)$/gm, '<li>$1</li>');
            
            // Wrap contiguous <li> blocks in <ul>
            html = html.replace(/(<li>.*?<\/li>\s*)+/g, function(match) {
                return '<ul>' + match + '</ul>';
            });
            
            // Links
            html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
            
            // Paragraphs (lines that aren't empty and aren't HTML elements)
            html = html.split('\n').map(line => {
                let trimmed = line.trim();
                if (!trimmed) return '';
                if (trimmed.startsWith('<h') || trimmed.startsWith('<pre') || trimmed.startsWith('</pre') || trimmed.startsWith('<ul') || trimmed.startsWith('</ul') || trimmed.startsWith('<li')) {
                    return line;
                }
                return '<p>' + line + '</p>';
            }).join('\n');
            
            return html;
        }

        async function runOrchestrator() {
            const taskInput = document.getElementById("task");
            const btnSubmit = document.getElementById("btnSubmit");
            const btnText = document.getElementById("btnText");
            const spinner = document.getElementById("spinner");
            const outputBody = document.getElementById("outputBody");
            const placeholder = document.getElementById("placeholder");
            const routedTag = document.getElementById("routedTag");

            const task = taskInput.value.trim();
            if (!task) {
                alert("Por favor ingresa una tarea.");
                return;
            }

            // UI Loading state
            btnSubmit.disabled = true;
            btnText.style.display = "none";
            spinner.style.display = "block";
            
            if (placeholder) {
                placeholder.style.display = "none";
            }
            outputBody.innerHTML = `<div style="color: var(--text-secondary); text-align: center; padding-top: 4rem;">
                <p>Nexus está analizando la tarea y convocando al agente idóneo...</p>
                <p style="font-size: 0.8rem; margin-top: 1rem; color: var(--accent-primary);">Invocando canal de procesamiento...</p>
            </div>`;

            try {
                const response = await fetch("/api/orchestrate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ task: task })
                });

                if (!response.ok) {
                    throw new Error("Respuesta de API incorrecta");
                }

                const result = await response.json();
                
                // Display routed tag
                routedTag.style.display = "inline-block";
                routedTag.innerText = result.routed_agent;
                if (result.routed_agent === "Bio-Agent") {
                    routedTag.style.borderColor = "var(--accent-secondary)";
                    routedTag.style.color = "var(--accent-secondary)";
                } else if (result.routed_agent === "Dev-Agent") {
                    routedTag.style.borderColor = "var(--success-color)";
                    routedTag.style.color = "var(--success-color)";
                } else {
                    routedTag.style.borderColor = "var(--accent-primary)";
                    routedTag.style.color = "var(--accent-primary)";
                }

                // Render content using Markdown-to-HTML helper
                outputBody.innerHTML = parseMarkdown(result.content);

            } catch (error) {
                outputBody.innerHTML = `<div style="color: #EF4444; padding: 1rem;">
                    <strong>Error de Orquestación:</strong><br>
                    ${error.message}. Por favor verifica que la API local esté corriendo.
                </div>`;
            } finally {
                btnSubmit.disabled = false;
                btnText.style.display = "block";
                spinner.style.display = "none";
            }
        }
    </script>
</body>
</html>
"""
    return html_content
