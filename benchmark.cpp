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

int main() {
    std::vector<int> vec;
    for (int i = 0; i < 50 * 1024 * 1024; i++) {
        vec.push_back(i * i + 1);
    }

    auto start = std::chrono::system_clock::now();

    for (int i = 0; i < 100; i++) {
        char *envp[] = {NULL};
        char *args[] = {
                "/usr/bin/sleep",
                "0",
                NULL};

        posix_spawnattr_t attr;
        CHECK(posix_spawnattr_init(&attr));
        CHECK(posix_spawnattr_setflags(&attr, POSIX_SPAWN_SETSIGDEF | POSIX_SPAWN_SETSIGMASK | POSIX_SPAWN_USEVFORK));

        pid_t pid;
        auto start_spawn = std::chrono::system_clock::now();
        CHECK(posix_spawn(
                &pid,
                "/usr/bin/sleep",
                NULL,
                &attr,
                &args[0],
                &envp[0]));
        waitpid(pid, NULL, 0);
        auto end = std::chrono::system_clock::now();
        auto diff = std::chrono::duration_cast<std::chrono::microseconds>(end - start_spawn).count();
        std::cout << diff << " us" << std::endl;
        CHECK(posix_spawnattr_destroy(&attr));
    }

    auto end = std::chrono::system_clock::now();
    auto diff = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << diff << " ms" << std::endl;

    std::cout << vec[1000] + vec[10231] << std::endl;

    return 0;
}
