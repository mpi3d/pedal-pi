#include <libwebsockets.h>
#include <string.h>
#include <signal.h>
#include <stdio.h>

static int callback_http(struct lws *wsi, enum lws_callback_reasons reason,
                         void *user, void *in, size_t len) {
    switch (reason) {
        case LWS_CALLBACK_ESTABLISHED:
            printf("Connected\n");
            break;

        case LWS_CALLBACK_RECEIVE: {
                //unsigned char *buf = (unsigned char*)
                    //malloc(LWS_SEND_BUFFER_PRE_PADDING + len +
                           //LWS_SEND_BUFFER_POST_PADDING);

                //for (int i; i < len; i++) {
                    //buf[LWS_SEND_BUFFER_PRE_PADDING + (len - 1) - i] = (
                            //(char *) in
                        //)[i];
                //}

                //unsigned char *buf = "hi";

                printf("Received data: %.*s\n", (int) len, (char *) in);
                //lws_write(wsi, &buf[LWS_SEND_BUFFER_PRE_PADDING],
                          //len, LWS_WRITE_TEXT);
                //free(buf);
                break;
            }

        default:
            break;
    }

    return 0;
}

static int interrupted;

static const struct lws_http_mount mount = {
    NULL, "/", "./", "index.html", NULL, NULL, NULL, NULL, 0, 0, 0, 0, 0, 0,
    LWSMPRO_FILE, 1, NULL
};

static struct lws_protocols protocols[] = {
    {"http", callback_http, 0},
    {NULL, NULL, 0, 0}
};

void signal_handler(int sig) {interrupted = 1;}

int main() {
    struct lws_context_creation_info info;
    struct lws_context *context;

    memset(&info, 0, sizeof info);

    info.port = 5555;
    info.mounts = &mount;
    info.protocols = protocols;

    context = lws_create_context(&info);

    if (!context) {
        printf("lws init failed\n");
        return 1;
    }

    signal(SIGINT, signal_handler);

    while (!interrupted) lws_service(context, 50);

    printf("\nShutdown...\n");
    lws_context_destroy(context);

    return 0;
}
