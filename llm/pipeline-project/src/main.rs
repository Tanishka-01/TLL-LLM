use std::{fs, process::{Command, Stdio}, io::Write};
use serde::Deserialize;
use std::sync::{Arc, OnceLock};
use clap::{Parser, Subcommand};

// Global static Arc to config
// This is needed for async processes to read config contents globally 
static CONFIG: OnceLock<Arc<Config>> = OnceLock::new();

// Change path to be in different locations other than just hard coded
//const CONFIG_PATH: &str = "./config.sh";
const CONFIG_PATH: &str = "config.toml";


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

#[derive(Deserialize, Debug)]
pub struct Config {
    pub python_env: String,
    pub log_file: String,
    pub enable_logging: bool,
    pub stt_model: String,
    pub stt_lang: String,
    pub llm_model: String,
    pub tts_model: String,
    pub output: String,
    pub audio_file: String,
}

impl Config {
    pub fn load(path: Option<String>) -> Result<Self, Box<dyn std::error::Error>> {
        let config_content = match path {
            Some(p) => fs::read_to_string(p)?,
            None => fs::read_to_string(CONFIG_PATH)?,
        };

        let config: Config = toml::from_str(&config_content)?;
        Ok(config)
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
        let log_entry = format!("\x1b[35m[{}]\x1b[0m {}\n", timestamp, message);
        
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
    println!("{:#?}", config);

    let mut cmd = Command::new(&config.python_env);
    cmd.args(["voice", "stt", "-m", &config.stt_model, "-l", &config.stt_lang]);

    let input_path = input.unwrap_or(&config.audio_file);
    let path = Path::new(input_path);

    // Validate that the path exists (or is a device)
    //if !path.exists() && !path.starts_with("/dev/") {
    //    return Err(format!("Input path does not exist: {}", input_path).into());
    //}
    cmd.arg(input_path);

    let output = cmd.output()
        .expect("\x1b[31mFailed to run Python script, make sure your in the correct working directory!!!\x1b[0m");
    
    if !output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        log(&format!("\x1b[31mSTT processing failed:\x1b[0m\n\nSTDOUT: {}\n\x1b[31mSTDERR: {}\x1b[0m", stdout, stderr));
        return Err("STT processing failed".into());
    }

    log("\x1b[32mSTT processing completed\x1b[0m");
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
        log(&format!("\x1b[31mLLM processing failed:\x1b[0m\n\nSTDOUT: {}\n\x1b[31mSTDERR: {}\x1b[0m", stdout, stderr));
        return Err("LLM processing failed".into());
    }

    log(&format!("\x1b[32mLLM processing completed\x1b[0m"));
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    Ok(stdout)
}


fn run_tts(input: &str) -> Result<String, Box<dyn std::error::Error>> {
    log("Starting TTS processing");
    let config = get_config();

    // this runs the subprocess 'voice' using the correct env
    let output = Command::new(&config.python_env)
        .args(["voice", "tts", input, "-v", &config.tts_model, "-o", &config.output])
        .output()?;

    if !output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        log(&format!("\x1b[31mTTS processing failed:\x1b[0m\n\nSTDOUT: {}\n\x1b[31mSTDERR: {}\x1b[0m", stdout, stderr));
        return Err("TTS processing failed".into());
    }

    log("\x1b[32mTTS processing completed\x1b[0m");
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    Ok(stdout)
}


fn main() -> Result<(), Box<dyn std::error::Error>> {
    // This is here so every crash is seprated by a log at the end in the log file
    let original_hook = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |panic_info| {
        println!("THERE IS AN ERROR!!!!!");
        log(&format!("\x1b[31mScript panicked and crashed\x1b[0m\n------------------------------------\n"));
        original_hook(panic_info);
    }));


    let args = Args::parse();

    // Load config
    let mut config = Config::load(args.config)?;
    if args.no_log {
        config.enable_logging = false;
    }
    CONFIG.set(Arc::new(config)).map_err(|_| "\x1b[33mConfig already initialized\x1b[0m")?;

    log("Script started");
    if let Some(command) = &args.command {
        let pipeline_output = match command {
            Commands::Stt { input } => {
                let output = run_stt(input.as_deref())?;
                output
            },
            Commands::Llm { input } => {
                let output = run_llm(input)?;
                output
            },
            Commands::Tts { input } => {
                let output = run_tts(input)?;
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
        println!("{pipeline_output}");
    } else {
        // Default full pipeline
        log("Running full pipeline");
        let audio_file = &get_config().audio_file;
        if !std::path::Path::new(audio_file).exists() {
            return Err(format!("Audio file does not exist: {}", audio_file).into());
        }
        let input = Some(audio_file.as_str());

        let stt_output = run_stt(input)?;
        let llm_output = run_llm(&stt_output)?;
        run_tts(&llm_output)?;
    }
    
    log(&format!("\x1b[32mScript execution completed\x1b[0m\n------------------------------------\n"));
    Ok(())
}
