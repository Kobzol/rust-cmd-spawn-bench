use clap::Parser;
use std::path::Path;
use std::process::Command;
use std::time::Instant;

fn make_commands(count: usize, binary: &str, set_env: bool) -> Vec<Command> {
    std::iter::from_fn(|| {
        let mut cmd = Command::new(binary);
        cmd.arg("0");
        if set_env {
            cmd.env("FOO", "BAR");
        }
        Some(cmd)
    })
    .take(count)
    .collect::<Vec<_>>()
}

fn add_envs_from_file(path: &Path) {
    let env_vars = std::fs::read_to_string(path).unwrap();
    for line in env_vars.lines() {
        let (key, value) = line.split_once("=").unwrap();
        std::env::set_var(key, value);
    }
}

#[derive(Parser)]
struct Args {
    name: String,
    #[arg(long)]
    alloc: Option<u64>,
    #[arg(long, default_value = "/usr/bin/sleep")]
    binary: String,
    #[arg(long)]
    set_env: bool,
}

fn main() {
    let args = Args::parse();

    // Normalize environment
    let keys = std::env::vars_os().map(|(k, _)| k).collect::<Vec<_>>();
    for key in keys {
        if key.to_str().unwrap() != "PATH" {
            std::env::remove_var(key);
        }
    }
    // Add fake environment variables
    // add_envs_from_file(Path::new("../envs.txt"));

    println!("name,process_count,env_count,mode,allocated,duration");

    let mut children = vec![];

    let mut allocated: Vec<u8> = vec![];
    let allocs = match args.alloc {
        Some(alloc) => (0..5).map(|i| alloc * 1024 * 1024).collect(),
        None => {
            vec![0]
        }
    };

    let name = args.name;
    let modes = ["spawn"];
    // let modes = ["spawn", "wait"];
    let counts = if allocs.len() == 1 {
        vec![10000] //, 5000, 10000, 25000]
    } else {
        vec![10000]
    };
    let env_increases = vec![50].repeat(5);
    let mut env_count = std::env::vars_os().count();

    let repeat_count = 3;

    for alloc in allocs {
        allocated.resize(allocated.len() + alloc as usize, alloc as u8);

        for env_incr in &env_increases {
            for _ in 0..*env_incr {
                std::env::set_var(format!("KEY_ENV_TEST_{}", env_count), "X".repeat(25));
                env_count += 1;
            }

            for process_count in &counts {
                for mode in modes {
                    for _ in 0..repeat_count {
                        assert!(children.is_empty());
                        let commands = make_commands(*process_count, &args.binary, args.set_env);

                        let start = Instant::now();
                        match mode {
                            "spawn" => {
                                for mut command in commands {
                                    let child = command.spawn().unwrap();
                                    children.push(child);
                                }
                            }
                            "wait" => {
                                for mut command in commands {
                                    command.spawn().unwrap().wait().unwrap();
                                }
                            }
                            _ => panic!(),
                        }

                        let duration = start.elapsed().as_secs_f64();
                        assert_eq!(std::env::vars_os().count(), env_count);
                        println!(
                            "{name},{process_count},{env_count},{mode},{},{duration}",
                            allocated.len()
                        );

                        for mut child in children.drain(..) {
                            child.wait().unwrap();
                        }
                    }
                }
            }
        }
    }

    eprintln!("{}", allocated.iter().sum::<u8>());
}
