#include <stdio.h>
#include <sys/time.h>

#define NB_SAMPLES 1000000

long double average_p1 = 0;
long double average_p2 = 0;

int ib;

char* value = "6547829";

int main() {
    struct timeval start, end;

    for (int i = 0; i < NB_SAMPLES; i++) {
        gettimeofday(&start, NULL);

        ib = 0;
        while(*value) {ib = ib * 10 + (*value++ - '0');};

        gettimeofday(&end, NULL);
        average_p1 += (end.tv_sec - start.tv_sec) + ((end.tv_usec - start.tv_usec) / 1000000.0);
        gettimeofday(&start, NULL);

        ib = 0;
        if (*value == '-') {value++;while(*value) {ib = ib * 10 + (*value++ - '0');}ib *= -1;}
        else while(*value) {ib = ib * 10 + (*value++ - '0');};

        gettimeofday(&end, NULL);
        average_p2 += (end.tv_sec - start.tv_sec) + ((end.tv_usec - start.tv_usec) / 1000000.0);
    }
    average_p1 /= NB_SAMPLES;
    average_p2 /= NB_SAMPLES;
    printf("Average program 1, Average program 2\n");
    printf("%10.10Lfs, %10.10Lfs\n", average_p1, average_p2);
    if (average_p1 < average_p2) printf("Program 1 is the fastest with %10.10Lfs less\n", average_p2 - average_p1);
    else if (average_p1 > average_p2) printf("Program 2 is the fastest with %10.10Lfs less\n", average_p1 - average_p2);
    else printf("Program 1 and Program 2 are equals\n");
    return 0;
}
