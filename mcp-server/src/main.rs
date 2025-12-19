use std::collections::HashMap;
use serde_json::Value;

// Represents a remote MCP server
#[derive(Debug, Clone)]
pub struct RemoteMcpServer {
    pub id: String,
    pub url: String,
}

// Enum to represent different capabilities
#[derive(Debug, Clone)]
pub enum Capability {
    Tool(Tool),
    Resource(Resource),
    Prompt(Prompt),
}

// Tool definition
#[derive(Debug, Clone)]
pub struct Tool {
    pub name: String,
    pub description: String,
    pub input_schema: Value,
    pub handler: Box<dyn Fn(Value) -> Result<Value, String>>,
}

// Resource definition (read-only data)
#[derive(Debug, Clone)]
pub struct Resource {
    pub name: String,
    pub description: String,
    pub path: String,
    pub handler: Box<dyn Fn() -> Result<String, String>>(),
}

// Prompt definition (template)
#[derive(Debug, Clone)]
pub struct Prompt {
    pub name: String,
    pub description: String,
    pub template: String,
    pub handler: Box<dyn Fn(Value) -> Result<Vec<Value>, String>>,
}

// Represents the MCP Server (main server struct)
pub struct McpServer {
    local_capabilities: HashMap<String, Capability>,
    remote_servers: HashMap<String, RemoteMcpServer>,
    resource_cache: HashMap<String, String>, // Local cache for resources
}

impl McpServer {
    // Initialize the server
    pub fn new() -> Self {
        Self {
            local_capabilities: HashMap::new(),
            remote_servers: HashMap::new(),
            resource_cache: HashMap::new(),
        }
    }

    // Register a capability (Tool, Resource, Prompt)
    pub fn register_capability(&mut self, capability: Capability) {
        match &capability {
            Capability::Tool(tool) => {
                self.local_capabilities.insert(tool.name.clone(), capability);
            }
            Capability::Resource(resource) => {
                self.local_capabilities.insert(resource.name.clone(), capability);
            }
            Capability::Prompt(prompt) => {
                self.local_capabilities.insert(prompt.name.clone(), capability);
            }
        }
    }

    // Add a remote server
    pub fn add_remote_server(&mut self, server: RemoteMcpServer) {
        self.remote_servers.insert(server.id.clone(), server);
    }

    // Centralized resource fetching (local or remote)
    pub fn fetch_capability(&self, name: &str) -> Result<String, String> {
        if let Some(capability) = self.local_capabilities.get(name) {
            return self.handle_local_capability(capability);
        }

        // Search remote servers if not found locally
        for (_, remote_server) in &self.remote_servers {
            return self.fetch_from_remote(remote_server, name);
        }

        Err(format!("Capability '{}' not found", name))
    }

    // Handle local capability fetching
    fn handle_local_capability(&self, capability: &Capability) -> Result<String, String> {
        match capability {
            Capability::Tool(tool) => {
                // For tools, we might want to execute some logic here
                Err(format!("Tool '{}' cannot be fetched directly", tool.name))
            }
            Capability::Resource(resource) => (resource.handler)(),
            Capability::Prompt(prompt) => {
                Err(format!("Prompt '{}' cannot be fetched directly", prompt.name))
            }
        }
    }

    // Fetch capability from remote server (placeholder logic for now)
    fn fetch_from_remote(&self, server: &RemoteMcpServer, name: &str) -> Result<String, String> {
        // This would involve making an HTTP request or MCP protocol call
        Err(format!("Fetching from remote server '{}' is not yet implemented", server.id))
    }

    // List all registered capabilities (tools, resources, prompts)
    pub fn list_capabilities(&self) -> Vec<String> {
        self.local_capabilities.keys().cloned().collect()
    }

    // Execute a tool (if it's a tool, execute it locally; otherwise, return error)
    pub fn execute_tool(&self, name: &str, input: Value) -> Result<Value, String> {
        if let Some(Capability::Tool(tool)) = self.local_capabilities.get(name) {
            return (tool.handler)(input);
        }
        Err(format!("Tool '{}' not found", name))
    }
}

