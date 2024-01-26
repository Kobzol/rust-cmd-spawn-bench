#include<unistd.h>
#include<signal.h>
#include<errno.h>
#include<fcntl.h>
#include<cassert>
#include<cstring>
#include<string>
#include<algorithm>
#include<vector>
#include<map>
#include<set>
#include<iostream>
#include<fstream>
#include<sstream>
#include<list>
using namespace std;

int foo(void*) {
    sleep(1);
    execlp("/usr/bin/sleep","/usr/bin/sleep", "0", (char*)NULL);
    return 0;
}

int single_talk(int thread_id){
    void *stack = malloc(4000) + 4000;
    fprintf(stderr,"thread %d before fork @%d\n",thread_id,time(0));
    int pid=clone(foo, stack, CLONE_VFORK | CLONE_VM, NULL);
    if(-1==pid){
        cerr << "failed to fork: " << strerror(errno) << endl;
        _exit(-3);//serious problem, can not proceed
    }
//    sleep(1);
    fprintf(stderr,"thread %d fork returned %d @%d\n",thread_id,pid,time(0));
    if(pid){//"CPP"
        fprintf(stderr,"thread %d in parent\n",thread_id);
    }else{//"PHP"
        sleep(1);
        fprintf(stderr,"thread %d in child @%d\n",thread_id,time(0));
        if(-1 == execlp("/usr/bin/sleep","/usr/bin/sleep", "0", (char*)NULL)){
            cerr << "failed to execl php : " << strerror(errno) << endl;
            _exit(-4);//serious problem, can not proceed
        }
    }
    return 0;
}
void * talker(void * id){
    single_talk(*(int*)id);
    return NULL;
}
int main(){
    signal(SIGPIPE,SIG_IGN);
    signal(SIGCHLD,SIG_IGN);
    const int thread_count = 44;
    pthread_t thread[thread_count];
    int thread_id[thread_count];
    int err;
    for(size_t i=0;i<thread_count;++i){
        thread_id[i]=i;
        if((err = pthread_create(thread+i,NULL,talker,thread_id+i))){
            cerr << "failed to create pthread: " << strerror(err) << endl;
            exit(-7);
        }
    }
    for(size_t i=0;i<thread_count;++i){
        if((err = pthread_join(thread[i],NULL))){
            cerr << "failed to join pthread: " << strerror(err) << endl;
            exit(-17);
        }
    }
}
