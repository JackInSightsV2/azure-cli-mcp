/**
 * Main JavaScript for Azure CLI MCP Server - Python Version
 */

// DOM ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Azure CLI MCP Server - Python Version loaded');
    
    // Add any initialization code here
    checkServerHealth();
});

/**
 * Check server health and display status
 */
async function checkServerHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        console.log('Server health check:', data);
        
        // Could add a status indicator to the page here
        // For now, just log the results
        
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

/**
 * Get server information
 */
async function getServerInfo() {
    try {
        const response = await fetch('/api/info');
        const data = await response.json();
        
        console.log('Server info:', data);
        return data;
        
    } catch (error) {
        console.error('Failed to get server info:', error);
        return null;
    }
}

// Export functions for potential use
window.AzureCliMcpServer = {
    checkServerHealth,
    getServerInfo
}; 