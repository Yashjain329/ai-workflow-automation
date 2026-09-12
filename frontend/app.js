// Dynamic API Base URL detection
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? '/api'
    : 'http://localhost:8000/api';

// WebSocket URL
const WS_BASE = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws';

document.addEventListener('DOMContentLoaded', () => {
    refreshDashboard();
    initWebSocket();
});

let ws = null;

function initWebSocket() {
    ws = new WebSocket(WS_BASE);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'update') {
                // Refresh the dashboard when we get an update from the server
                refreshDashboard();
            }
        } catch (e) {
            console.error('Error parsing WebSocket message:', e);
        }
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected. Attempting to reconnect...');
        // Try to reconnect after 3 seconds
        setTimeout(initWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

async function refreshDashboard() {
    try {
        await Promise.all([
            fetchMetrics(),
            fetchApprovalQueue(),
            fetchJobsList()
        ]);
    } catch (e) {
        console.error('Error in refreshDashboard:', e);
    }
}

// We'll keep the fetch functions as they are, but we can remove the polling interval
// since we are now using WebSocket for updates.

async function fetchMetrics() {
    try {
        const res = await fetch(`${API_BASE}/monitoring/metrics`); // Note: changed to /monitoring/metrics
        const data = await res.json();
        
        document.getElementById('stat-total').innerText = data.total_jobs || 0;
        document.getElementById('stat-auto-rate').innerText = `${(data.automation_rate || 0) * 100}%`;
        document.getElementById('stat-pending').innerText = data.pending_approvals || 0;
        document.getElementById('stat-avg-conf').innerText = (data.avg_confidence || 0).toFixed(2);
    } catch (e) {
        console.error('Error fetching metrics:', e);
        // Optionally, we can set default values or show an error state
    }
}

async function fetchApprovalQueue() {
    try {
        const res = await fetch(`${API_BASE}/approvals`);
        const tasks = await res.json();
        
        const container = document.getElementById('approval-list');
        document.getElementById('approval-badge').innerText = `${tasks.length} tasks`;
        
        if (tasks.length === 0) {
            container.innerHTML = `<p class=\"text-xs text-slate-500 italic py-4 text-center\">No tasks currently awaiting human review.</p>`;
            return;
        }
        
        container.innerHTML = tasks.map(task => `
            <div class=\"bg-slate-900 border border-amber-500/30 rounded-lg p-3.5 space-y-2\">
                <div class=\"flex justify-between items-center\">
                    <span class=\"font-bold text-amber-400 text-xs\">${task.task_id}</span>
                    <span class=\"text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded\">Conf: ${(task.confidence * 100).toFixed(0)}%</span>
                </div>
                <p class=\"text-xs text-slate-300\">${task.reason}</p>
                <div class=\"flex space-x-2 pt-2\">
                    <button onclick=\"handleApproval('${task.task_id}', 'APPROVED')\" class=\"flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-1.5 rounded text-[11px] transition-colors\">Approve</button>
                    <button onclick=\"handleApproval('${task.task_id}', 'REJECTED')\" class=\"flex-1 bg-rose-600 hover:bg-rose-500 text-white font-semibold py-1.5 rounded text-[11px] transition-colors\">Reject</button>
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Error fetching approval queue:', e);
    }
}

async function fetchJobsList() {
    try {
        const res = await fetch(`${API_BASE}/jobs`);
        const jobs = await res.json();
        
        const tbody = document.getElementById('jobs-table-body');
        if (jobs.length === 0) {
            tbody.innerHTML = `<tr><td colspan=\"6\" class=\"px-4 py-8 text-center text-slate-500\">No workflow jobs recorded yet.</td></tr>`;
            return;
        }
        
        tbody.innerHTML = jobs.map(j => `
            <tr class=\"hover:bg-slate-700/30 transition-colors\">
                <td class=\"px-4 py-3 font-mono font-semibold text-indigo-300\">${j.job_id}</td>
                <td class=\"px-4 py-3 capitalize\">${j.category}</td>
                <td class=\"px-4 py-3\">${getStatusBadge(j.status)}</td>
                <td class=\"px-4 py-3\">${j.human_intervention ? '<span class=\"text-amber-400 font-semibold\">Yes</span>' : '<span class=\"text-slate-500\">Auto</span>'}</td>
                <td class=\"px-4 py-3 text-slate-400\">${new Date(j.created_at).toLocaleTimeString()}</td>
                <td class=\"px-4 py-3 text-right\">
                    <button onclick=\"inspectJob('${j.job_id}')\" class=\"text-indigo-400 hover:text-indigo-300 font-semibold text-[11px]\">Inspect →</button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        console.error('Error fetching jobs:', e);
    }
}

function getStatusBadge(status) {
    if (status === 'AUDITED' || status === 'COMPLETED') {
        return `<span class=\"bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded text-[10px] font-semibold\">${status}</span>`;
    } else if (status === 'APPROVAL_PENDING') {
        return `<span class=\"bg-amber-500/20 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded text-[10px] font-semibold\">${status}</span>`;
    } else if (status === 'FAILED') {
        return `<span class=\"bg-rose-500/20 text-rose-400 border border-rose-500/30 px-2 py-0.5 rounded text-[10px] font-semibold\">${status}</span>`;
    }
    return `<span class=\"bg-slate-700 text-slate-300 px-2 py-0.5 rounded text-[10px]\">${status}</span>`;
}

async function handleApproval(taskId, decision) {
    try {
        await fetch(`${API_BASE}/approvals/${taskId}/decision`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decision, reviewer: 'human_operator' })
        });
        // The WebSocket will trigger a refresh, but we can also refresh immediately for better UX
        refreshDashboard();
    } catch (e) {
        alert('Error submitting approval decision');
        console.error('Error submitting approval:', e);
    }
}

function showSubmitModal() {
    document.getElementById('submit-modal').classList.remove('hidden');
}

function closeSubmitModal() {
    document.getElementById('submit-modal').classList.add('hidden');
}

async function submitNewJob() {
    const source = document.getElementById('input-source').value;
    const raw_payload = document.getElementById('input-payload').value;

    if (!raw_payload.trim()) {
        alert('Please enter a payload text.');
        return;
    }

    try {
        await fetch(`${API_BASE}/jobs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source, raw_payload })
        });
        closeSubmitModal();
        document.getElementById('input-payload').value = '';
        // The WebSocket will trigger a refresh, but we can also refresh immediately for better UX
        refreshDashboard();
    } catch (e) {
        alert('Error submitting job');
        console.error('Error submitting job:', e);
    }
}

async function inspectJob(jobId) {
    try {
        const res = await fetch(`${API_BASE}/jobs/${jobId}`);
        const data = await res.json();

        document.getElementById('modal-job-id').innerText = `Job Trace: ${jobId}`;
        const content = document.getElementById('modal-detail-content');

        content.innerHTML = `
            <div class=\"bg-slate-900 p-3 rounded border border-slate-700 space-y-1\">
                <p class=\"font-semibold text-slate-300\">Raw Input:</p>
                <p class=\"font-mono text-slate-400 break-words\">${data.job.raw_payload || 'N/A'}</p>
            </div>

            <div class=\"grid grid-cols-2 gap-3\">
                <div class=\"bg-slate-900 p-3 rounded border border-slate-700\">
                    <p class=\"font-semibold text-slate-300\">ML Prediction:</p>
                    <p class=\"text-indigo-400 font-bold mt-1\">${data.prediction?.predicted_category || 'N/A'}</p>
                    <p class=\"text-slate-400\">Confidence: ${(data.prediction?.confidence * 100 || 0).toFixed(0)}%</p>
                    <p class=\"text-[10px] text-slate-500 mt-1\">Fields: ${JSON.stringify(data.prediction?.extracted_fields || {})}</p>
                </div>
                <div class=\"bg-slate-900 p-3 rounded border border-slate-700\">
                    <p class=\"font-semibold text-slate-300\">Policy Decision:</p>
                    <p class=\"text-amber-400 font-bold mt-1\">${data.decision?.route || 'N/A'}</p>
                    <p class=\"text-slate-400\">Risk Level: ${data.decision?.risk_level || 'N/A'}</p>
                    <p class=\"text-[10px] text-slate-500 mt-1\">${data.decision?.explanation || ''}</p>
                </div>
            </div>

            <div class=\"bg-slate-900 p-3 rounded border border-slate-700 space-y-2\">
                <p class=\"font-semibold text-slate-300\">Execution Log:</p>
                ${data.action_logs.map(l => \`
                    <div class=\"flex justify-between text-[11px] border-b border-slate-800 pb-1\">
                        <span class=\"text-slate-400\">${l.connector}</span>
                        <span class=\${l.status === 'SUCCESS' ? 'text-emerald-400' : 'text-rose-400'}\">${l.status}</span>
                    </div>
                \`).join('') || '<p class=\"text-slate-500\">No actions executed yet.</p>'}
            </div>
        `;

        document.getElementById('detail-modal').classList.remove('hidden');
    } catch (e) {
        alert('Error fetching job details');
        console.error('Error inspecting job:', e);
    }
}

function closeDetailModal() {
    document.getElementById('detail-modal').classList.add('hidden');
}