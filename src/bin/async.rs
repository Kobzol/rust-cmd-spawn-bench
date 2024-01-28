use clap::Parser;
use std::time::Instant;

async fn spawn(mode: Mode) {
    let mut cmd = tokio::process::Command::new("/usr/bin/sleep");
    // cmd.env("FOO", "BAR");
    cmd.arg("0");
    match mode {
        Mode::Single | Mode::Multi => {
            cmd.spawn().unwrap();
        }
        Mode::SingleBlocking => {
            tokio::task::spawn_blocking(move || {
                cmd.spawn().unwrap();
            })
            .await
            .unwrap();
        }
    }
}

#[derive(clap::ValueEnum, Clone, Copy, Debug)]
enum Mode {
    Multi,
    Single,
    SingleBlocking,
}

#[derive(Parser)]
struct Args {
    name: String,
    mode: Mode,
    #[arg(long, default_value = "1")]
    thread_count: usize,
}

fn main() {
    let Args {
        name,
        mode,
        thread_count,
    } = Args::parse();

    let mut runtime = match mode {
        Mode::Multi => {
            let mut runtime = tokio::runtime::Builder::new_multi_thread();
            runtime.worker_threads(thread_count);
            runtime
        }
        Mode::Single | Mode::SingleBlocking => tokio::runtime::Builder::new_current_thread(),
    };

    let runtime = runtime.enable_all().build().unwrap();

    let process_count = 20000;
    let repeat_count = 3;

    println!("name,process_count,mode,thread_count,duration");

    for _ in 0..repeat_count {
        let mut tasks = Vec::with_capacity(process_count);

        let start = Instant::now();
        runtime.block_on(async {
            for _ in 0..process_count {
                tasks.push(tokio::spawn(spawn(mode)));
            }
            futures::future::join_all(tasks).await;
        });
        let duration = start.elapsed().as_secs_f64();
        println!("{name},{process_count},{mode:?},{thread_count},{duration}");
    }
}
