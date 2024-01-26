use std::time::Instant;

async fn spawn() {
    let mut cmd = tokio::process::Command::new("sleep");
    cmd.arg("0");
    // tokio::task::spawn_blocking(move || {
        cmd.spawn().unwrap();
    // }).await.unwrap();
}

fn main() {
    let mut runtime = tokio::runtime::Builder::new_current_thread();
    // let mut runtime = tokio::runtime::Builder::new_multi_thread();
    // runtime.worker_threads(16);

    let runtime = runtime.enable_all().build().unwrap();
    let mut tasks = Vec::with_capacity(1000);

    let start = Instant::now();
    runtime.block_on(async move {
        for i in 0..100 {
            tasks.push(tokio::spawn(spawn()));
        }
        for t in tasks {
            t.await.unwrap();
        }
    });
    println!("{}", start.elapsed().as_secs_f64());
}
