#include <chrono>
#include <iostream>
#include <spawn.h>
#include <vector>
#include <sys/wait.h>

#define CHECK(err)                         \
    {                                      \
        int ret = err;                     \
        if (ret != 0) {                    \
            errno = ret;                   \
            std::cerr << ret << std::endl; \
            perror("fail");                \
            exit(1);                       \
        }                                  \
    }

int main(int argc, char** argv) {
    std::vector<uint8_t> allocated;

    if (argc < 4) {
        return 1;
    }

    const char* name = argv[1];
    int alloc = std::stoi(argv[2]);
    bool use_vfork = std::stoi(argv[3]) == 1;

    auto start = std::chrono::system_clock::now();

    std::vector<int> counts = {1000, 5000, 10000, 25000};
    int repeat_count = 3;

    std::cout << "name,process_count,env_count,mode,vfork,allocated,duration" << std::endl;

    std::vector<int> alloc_increments;
    if (alloc == 0) {
        alloc_increments.push_back(0);
    } else {
        alloc_increments = {alloc, alloc, alloc, alloc, alloc};
        counts = {10000};
    }

    int flags = POSIX_SPAWN_SETSIGDEF | POSIX_SPAWN_SETSIGMASK;
    if (use_vfork) {
        flags |= POSIX_SPAWN_USEVFORK;
    }

    std::vector<pid_t> processes;
    for (auto alloc_increment: alloc_increments) {
        allocated.resize(allocated.size() + (alloc_increment * 1024 * 1024));

        for (const auto& process_count: counts) {
            for (int i = 0; i < repeat_count; i++) {
                processes.clear();

                auto start = std::chrono::system_clock::now();
                for (int p = 0; p < process_count; p++) {
                    pid_t pid;

                    char *envp[] = {NULL};
                    char *args[] = {
                        "/usr/bin/sleep",
                        "0",
                        NULL};

                    posix_spawnattr_t attr;
                    CHECK(posix_spawnattr_init(&attr));
                    CHECK(posix_spawnattr_setflags(&attr, flags));

                    CHECK(posix_spawn(
                        &pid,
                        "/usr/bin/sleep",
                        NULL,
                        &attr,
                        &args[0],
                        &envp[0]));
                    processes.push_back(pid);
                    CHECK(posix_spawnattr_destroy(&attr));
                }
                auto end = std::chrono::system_clock::now();
                auto duration_ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
                double duration = static_cast<double>(duration_ms) / 1000.0;
                std::cout << name << "-cpp," << process_count << ",1,spawn," << (use_vfork ? '1' : '0') << "," << allocated.size() << "," << duration << std::endl;

                for (auto pid: processes) {
                    waitpid(pid, NULL, 0);
                }
            }
        }
    }

    if (!allocated.empty()) {
        std::cout << (int) allocated[alloc - 1] << std::endl;
    }

    return 0;
}
