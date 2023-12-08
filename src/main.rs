use std::process::Command;
use std::time::Instant;

static FILE: &str = include_str!("../envs.txt");

fn make_commands(count: usize) -> Vec<Command> {
    std::iter::from_fn(|| {
        let mut cmd = Command::new("/usr/bin/sleep");
        cmd.env("FOO", "BAR");
        cmd.arg("0");
        Some(cmd)
    })
    .take(count)
    .collect::<Vec<_>>()
}

fn main() {
    let process_count = 8000;
    let repeat_count = 1;

    // Normalize environment
    let keys = std::env::vars_os().map(|(k, _)| k).collect::<Vec<_>>();
    for key in keys {
        if key.to_str().unwrap() != "PATH" {
            std::env::remove_var(key);
        }
    }
    // Add fake environment variables
    for line in FILE.lines() {
        let (key, value) = line.split_once("=").unwrap();
        std::env::set_var(key, value);
    }

    let mut children = vec![];
    for _ in 0..repeat_count {
        let commands = make_commands(process_count);
        children.clear();

        let start = Instant::now();
        for mut command in commands {
            let child = command.spawn().unwrap();
            children.push(child);
        }
        let duration = start.elapsed().as_secs_f64();
        println!("{duration}");

        for mut child in children.drain(..) {
            child.wait().unwrap();
        }
    }
}
