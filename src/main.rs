use std::path::Path;
use std::process::Command;
use std::time::Instant;
use clap::Parser;

fn make_commands(count: usize) -> Vec<Command> {
    std::iter::from_fn(|| {
        let mut cmd = Command::new("/usr/bin/sleep");
        cmd.arg("0");
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
    name: String
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

    println!("name,process_count,env_count,mode,duration");

    let mut children = vec![];

    let name = args.name;
    let modes = ["spawn"];
    // let modes = ["spawn", "wait"];
    let counts = [1000, 5000, 10000, 25000];

    let repeat_count = 10;
    let env_count = std::env::vars_os().count();

    for process_count in counts {
        for mode in modes {
            for _ in 0..repeat_count {
                assert!(children.is_empty());
                let commands = make_commands(process_count);

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
                    _ => panic!()
                }

                let duration = start.elapsed().as_secs_f64();
                println!("{name},{process_count},{env_count},{mode},{duration}");

                for mut child in children.drain(..) {
                    child.wait().unwrap();
                }
            }
        }
    }
}
