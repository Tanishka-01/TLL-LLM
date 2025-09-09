use std::{fs, process::{Command, Stdio}, io::Write};
use clap::{Parser, Subcommand};
use std::sync::{Arc, OnceLock};

// Global static Arc to config
// This is needed for async processes to read config contents globally 
static CONFIG: OnceLock<Arc<Config>> = OnceLock::new();

// Change path to be in different locations other than just hard coded
const CONFIG_PATH: &str = "./config.sh";


#[derive(Parser)]
#[clap(name = "pipeline", about = "Pipeline runner for STT-LLM-TTS processing")]
struct Args {
    // config file location
    #[clap(short = 'c', long = "config", help = "Config file path")]
    config: Option<String>,

    // disable logging
    #[clap(short = 'n', long = "no-log", help = "Disable logging")]
    no_log: bool,
    
    #[clap(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    #[clap(about = "Run speech-to-text only")]
    Stt {
        #[clap(help = "Input audio file or device (e.g., 'input.wav' or '/dev/audio')")]
        input: Option<String>,
    },
    #[clap(about = "Run LLM processing")]
    Llm {
        #[clap(help = "Input text for LLM")]
        input: String,
    },
    #[clap(about = "Run text-to-speach only")]
    Tts {
        #[clap(help = "Input text for TTS")]
        input: String,
    },
}

pub struct Config {
    pub python_env: String,
    pub log_file: String,
    pub enable_logging: bool,
    pub stt_model: String,
    pub stt_lang: String,
    pub llm_model: String,
    pub tts_model: String,
    pub output: String,
}
impl Config {
    fn load(path: Option<String>) -> Result<Self, Box<dyn std::error::Error>> {
        let config_content = match path {
            Some(p) => fs::read_to_string(p)?,
            None => fs::read_to_string(CONFIG_PATH)?,
        };

        let mut stt_model = String::new();
        let mut stt_lang = String::new();
        let mut llm_model = String::new();
        let mut tts_model = String::new();
        let mut output = String::new();
        let mut python_env = String::new();
        let mut log_file = "pipeline.log".to_string();
        let mut enable_logging = true;

        // this is bad code however I'm not certain theres a better way without importing a parser of some type
        for line in config_content.lines() {
            if line.starts_with("STT_MODEL=") {
                stt_model = line[10..].trim_matches('"').to_string();
            } else if line.starts_with("STT_LANG=") {
                stt_lang = line[9..].trim_matches('"').to_string();
            } else if line.starts_with("LLM_MODEL=") {
                llm_model = line[10..].trim_matches('"').to_string();
            } else if line.starts_with("TTS_MODEL=") {
                tts_model = line[10..].trim_matches('"').to_string();
            } else if line.starts_with("OUTPUT=") {
                output = line[7..].trim_matches('"').to_string();
            } else if line.starts_with("PYTHON_ENV=") {
                python_env = line[11..].trim_matches('"').to_string();
            } else if line.starts_with("LOG_FILE=") {
                log_file = line[9..].trim_matches('"').to_string();
            } else if line.starts_with("ENABLE_LOGGING=") {
                enable_logging = line[15..].trim_matches('"').parse().expect("Some bool if logging");
            }
        }

        Ok(Config {
            stt_model,
            stt_lang,
            llm_model,
            tts_model,
            output,
            python_env,
            log_file,
            enable_logging,
        })
    }
}
// Helper to get the global config (safe for both sync and async)
fn get_config() -> &'static Arc<Config> {
    CONFIG.get().expect("Config not initialized")
}


fn log(message: &str) {
    let config = get_config();
    if config.enable_logging {
        let timestamp = chrono::Local::now().format("%Y-%m-%d %H:%M:%S.%3f").to_string();
        let log_entry = format!("[{}] {}\n", timestamp, message);
        
        // Create or Append to log file
        let mut file = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&config.log_file)
            .expect("Failed to open/create log file");
        writeln!(file, "{}", log_entry).unwrap();
    }
}



fn run_stt(input: Option<&str>) -> Result<String, Box<dyn std::error::Error>> {
    use std::path::Path;
    
    log("Starting STT processing");
    let config = get_config();

    let mut cmd = Command::new("python-env/bin/python");
    cmd.args(["voice", "stt", "-m", &config.stt_model, "-l", &config.stt_lang]);

    if let Some(input_path) = input {
        let path = Path::new(input_path);

        // Validate that the path exists (or is a device)
        if !path.exists() && !path.starts_with("/dev/") {
            return Err(format!("Input path does not exist: {}", input_path).into());
        }

        cmd.arg(input_path);
    }

    let output = cmd.output()
        .expect("Failed to run Python script, make sure your in the correct working directory!!!");
    
    if !output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        log(&format!("STT processing failed:\n\nSTDOUT: {}\nSTDERR: {}", stdout, stderr));
        return Err("STT processing failed".into());
    }
    
    log("STT processing completed");
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    Ok(stdout)
}


fn run_llm(input: &str) -> Result<String, Box<dyn std::error::Error>> {
    log("Starting LLM processing");
    let config = get_config();
    
    let mut child = Command::new("ollama")
        .args(["run", &config.llm_model, input])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;

    if let Some(ref mut stdin) = child.stdin {
        stdin.write_all(input.as_bytes())?;
    }
    
    let output = child.wait_with_output()?;

    
    if !output.status.success()/*.wait()?.success()*/ {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        log(&format!("LLM processing failed:\n\nSTDOUT: {}\nSTDERR: {}", stdout, stderr));
        return Err("LLM processing failed".into());
    }
    
    log("LLM processing completed");
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    Ok(stdout)
}


fn run_tts(input: &str) -> Result<String, Box<dyn std::error::Error>> {
    log("Starting TTS processing");
    let config = get_config();
    
    // this runs the subprocess 'voice' using the correct env
    let output = Command::new("python-env/bin/python")
        .args(["voice", "tts", input, "-v", &config.tts_model, "-o", &config.output])
        .output()?;
    
    if !output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        log(&format!("TTS processing failed:\n\nSTDOUT: {}\nSTDERR: {}", stdout, stderr));
        return Err("TTS processing failed".into());
    }
    
    log("TTS processing completed");
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    Ok(stdout)
}



fn main() -> Result<(), Box<dyn std::error::Error>> {
    let original_hook = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |panic_info| {
        log("Script panicked and crashed\n------------------------------------\n");
        original_hook(panic_info);
    }));

    let args = Args::parse();

    // Load config
    let mut config = Config::load(args.config)?;
    if args.no_log {
        config.enable_logging = false;
    }
    CONFIG.set(Arc::new(config)).map_err(|_| "Config already initialized")?;
    
    log("Script started");
    // need to fix in future so that output from one goes into another
    if let Some(command) = &args.command {
        let _balls = match command {
            Commands::Stt { input} => {
                //let input = false;
                let output = run_stt(input.as_deref())?;
                println!("STT output: {output}");
                output
            },
            Commands::Llm { input} => {
                let output = run_llm(input)?;
                //println!("LLM output: {output}");
                output
            },
            Commands::Tts { input } => {
                let output = run_tts(input)?;
                //println!("TTS output: {output}");
                output
            },
            /*
            _ => {
                // Default full pipeline
                log("Running full pipeline");
                let input = Some("hey whats going on");

                let stt_output = run_stt(input)?;
                let llm_output = run_llm(&stt_output)?;
                run_tts(&llm_output)?        
            }
            */
        };
        //println!("{balls}");
    } else {
        // Default full pipeline
        log("Running full pipeline");
        let input = Some("llm-output.wav");

        let stt_output = run_stt(input)?;
        let llm_output = run_llm(&stt_output)?;
        run_tts(&llm_output)?;
    }
    
    log("Script execution completed\n------------------------------------\n");
    Ok(())
}