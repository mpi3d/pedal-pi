#include <bcm2835.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

#include "httpd.h"

int main() {
    pthread_t thread_id;
    pthread_create(&thread_id, NULL, &serve_forever, "8000");
    serve_forever("8080");
    return 0;
}

void route() {
    ROUTE_START()

    ROUTE_GET("/") {
        printf("HTTP/1.1 200 OK\r\n\r\n");
        printf("Hello! You are using %s", request_header("User-Agent"));
    }

    ROUTE_GET("/test") {
        printf("HTTP/1.1 200 OK\r\n\r\n");
        printf("List of request headers:\r\n\r\n");

        header_t *h = request_headers();

        while (h->name) {
            printf("%s: %s\n", h->name, h->value);
            h++;
        }
    }

    ROUTE_POST("/") {
        printf("HTTP/1.1 200 OK\r\n\r\n");
        printf("Wow, seems that you POSTed %d bytes. \r\n", payload_size);
        printf("Fetch the data using `payload` variable.");
    }

    ROUTE_END()
}
