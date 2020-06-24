from http.server import BaseHTTPRequestHandler, HTTPServer
from os import system, curdir, path, walk
from json import load
from pexpect import spawn
from paho.mqtt.client import Client

print("Starting...")


class Page(BaseHTTPRequestHandler):
    def do_GET(self):
        if "paho-mqtt.js" in self.path:
            self.send_response(200)
            self.send_header("Content-type", "application/javascript")
            self.end_headers()
            mqtt_js = open(path.join(curdir, "paho-mqtt.js"))
            self.wfile.write(bytes(mqtt_js.read(), "utf-8"))
            mqtt_js.close()
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(HTML, "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def message(_mqtt, _data, msg):
    PEDAL.sendline(msg.payload.decode("utf-8"))
    if not PEDAL.isalive():
        print("ChildProcessError: pedal_pi is not running")
        PEDAL.close()
        MQTT.loop_stop()
        SERVER.shutdown()


INCLUDES = ""
INITS = ""
VARS = ""
TIMER = ""
EFFECTS = ""

for paths, dirs, files in walk(path.join(curdir, "effects")):
    for file in files:
        file_path = path.join(paths, file)
        if path.splitext(file_path)[1] == ".json":
            file = open(file_path)
            JSON = load(file)
            file.close()
            if not "active" in JSON:
                JSON["active"] = True
            if JSON["active"]:
                if not "Path" in JSON["program"]:
                    JSON["program"]["path"] = None
                if JSON["program"]["path"] is not None:
                    INCLUDES += '#include "' + JSON["program"]["path"] + '"\n'
                if not "setup" in JSON["program"]:
                    JSON["program"]["setup"] = None
                if JSON["program"]["setup"] is not None:
                    INITS += JSON["program"]["setup"]
                if not "timer" in JSON["program"]:
                    JSON["program"]["timer"] = None
                if JSON["program"]["timer"] is not None:
                    TIMER += JSON["program"]["timer"]
                if not "effect" in JSON["program"]:
                    JSON["program"]["effect"] = None
                if JSON["program"]["effect"] is not None:
                    if EFFECTS != "":
                        EFFECTS += "else "
                    EFFECTS += "if (0) {" + JSON["program"]["effect"] + "}"
                for KEY, VALUE in JSON["input"].items():
                    if not "type" in VALUE:
                        VALUE["type"] = "button"
                    if VALUE["type"] == "button":
                        if not "toggle" in VALUE:
                            VALUE["toggle"] = False
                        if VARS != "":
                            VARS += "else "
                        VARS += (
                            'if (strcmp(value, "'
                            + KEY
                            + "\")) {if ((char)*value == '0') "
                            + KEY
                            + " = FALSE;else "
                            + KEY
                            + " = TRUE;}"
                        )
                        INITS += "bool " + KEY + " = FALSE;"
                    elif VALUE["type"] == "potentiometer" or VALUE["type"] == "slider":
                        if not "min" in VALUE:
                            VALUE["min"] = 0
                        if not "max" in VALUE:
                            VALUE["max"] = 4095
                        if not "start" in VALUE:
                            VALUE["start"] = VALUE["min"]
                        if not isinstance(VALUE["min"], int):
                            raise TypeError("In '" + KEY + "' 'min' value must be int")
                        if not isinstance(VALUE["max"], int):
                            raise TypeError("In '" + KEY + "' 'max' value must be int")
                        if not isinstance(VALUE["start"], int):
                            raise TypeError("In '" + KEY + "' 'start' value must be int")
                        if VALUE["min"] >= VALUE["max"]:
                            raise ValueError(
                                "In '" + KEY + "' 'min' value must be smaller than 'max' value"
                            )
                        if VALUE["start"] < VALUE["min"] or VALUE["start"] > VALUE["max"]:
                            raise ValueError(
                                "In '"
                                + KEY
                                + "' 'start' value must be beetew \
                                             'min' and 'max' value"
                            )
                        if VALUE["min"] > -1:
                            if VALUE["max"] < 256:
                                VAR_TYPE = "uint_fast8_t"
                            elif VALUE["max"] < 65536:
                                VAR_TYPE = "uint_fast16_t"
                            elif VALUE["max"] < 4294967296:
                                VAR_TYPE = "uint_fast32_t"
                            elif VALUE["max"] < 18446744073709551616:
                                VAR_TYPE = "uint_fast64_t"
                            else:
                                raise ValueError(
                                    "In '"
                                    + KEY
                                    + "' 'max' value must be smaller \
                                                 than 18446744073709551616"
                                )
                            if VARS != "":
                                VARS += "else "
                            VARS += (
                                'if (strcmp(value, "'
                                + KEY
                                + '")) {'
                                + KEY
                                + " = 0;while(*value) {"
                                + KEY
                                + " = "
                                + KEY
                                + " * 10 + (*value++ - '0');}}"
                            )
                        else:
                            if VALUE["min"] > -129 and VALUE["max"] < 128:
                                VAR_TYPE = "int_fast8_t"
                            elif VALUE["min"] > -32769 and VALUE["max"] < 32768:
                                VAR_TYPE = "int_fast16_t"
                            elif VALUE["min"] > -2147483649 and VALUE["max"] < 2147483648:
                                VAR_TYPE = "int_fast32_t"
                            elif (
                                VALUE["min"] > -9223372036854775809
                                and VALUE["max"] < 9223372036854775808
                            ):
                                VAR_TYPE = "int_fast64_t"
                            elif VALUE["min"] < -9223372036854775808:
                                raise ValueError(
                                    "In '"
                                    + KEY
                                    + "' 'min' value must be greater \
                                                 than -9223372036854775808"
                                )
                            else:
                                raise ValueError(
                                    "In '"
                                    + KEY
                                    + "' 'max' value must be smaller \
                                                 than 9223372036854775807"
                                )
                            if VARS != "":
                                VARS += "else "
                            VARS += (
                                'if (strcmp(value, "'
                                + KEY
                                + '")) {'
                                + KEY
                                + " = 0;if (*value == '-') {value++;while(*value) {"
                                + KEY
                                + " = "
                                + KEY
                                + " * 10 + (*value++ - '0');}"
                                + KEY
                                + " *= -1;}else while(*value) {"
                                + KEY
                                + " = "
                                + KEY
                                + " * 10 + (*value++ - '0');};}"
                            )
                        INITS += VAR_TYPE + " " + KEY + " = " + str(VALUE["start"]) + ";"
                        if VALUE["type"] == "potentiometer":
                            if not "min deg" in VALUE:
                                VALUE["min deg"] = -135
                            if not "max deg" in VALUE:
                                VALUE["max deg"] = 135
                            if not isinstance(VALUE["min deg"], int):
                                raise TypeError("In '" + KEY + "' 'min deg' value must be int")
                            if not isinstance(VALUE["max deg"], int):
                                raise TypeError("In '" + KEY + "' 'max deg' value must be int")
                        elif VALUE["type"] == "slider":
                            pass
                    elif VALUE["type"] == "switch":
                        if not VALUE["positions"]:
                            VALUE["positions"] = 2
                        if not VALUE["start"]:
                            VALUE["start"] = 1
                        if not isinstance(VALUE["positions"], int):
                            raise TypeError("In '" + KEY + "' 'positions' value must be int")
                        if not isinstance(VALUE["start"], int):
                            raise TypeError("In '" + KEY + "' 'start' value must be int")
                        if VALUE["start"] < 1 or VALUE["start"] > VALUE["positions"]:
                            raise ValueError(
                                "In '"
                                + KEY
                                + "' 'start' value must be beetew \
                                             1 and 'positions' value"
                            )
                        if VARS != "":
                            VARS += "else "
                        VARS += (
                            'if (strcmp(value, "'
                            + KEY
                            + '")) {'
                            + KEY
                            + " = 0;while(*value) {"
                            + KEY
                            + " = "
                            + KEY
                            + " * 10 + (*value++ - '0');}}"
                        )
                    else:
                        raise ValueError("In '" + KEY + "' unknow value for 'type'")


HTML = """
<!DOCTYPE html>
<html>
    <body>
        <script src="paho-mqtt.js"></script>
        <script>
            var client = new Paho.Client(location.hostname, 1884, "pedal_pi");

            client.onMessageArrived = message;
            client.connect({userName:"pedal_pi", password:"~Effect~", onSuccess:connect});

            function connect() {
                client.subscribe("pedal_pi");
                message = new Paho.Message("test=test");
                message.destinationName = "pedal_pi";
                client.send(message);
            }

            function message(message) {
                console.log("You have send " + message.payloadString);
            }
        </script>
    </body>
</html>
"""

C = (
    """
#include <bcm2835.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
"""
    + INCLUDES
    + """
#define FALSE  0
#define TRUE   1
#define LED            RPI_V2_GPIO_P1_36
#define PUSH_1         RPI_GPIO_P1_08
#define PUSH_2         RPI_V2_GPIO_P1_38
#define TOGGLE_SWITCH  RPI_V2_GPIO_P1_32
#define FOOT_SWITCH    RPI_GPIO_P1_10

typedef uint8_t bool;

uint8_t push_1_val;uint8_t push_2_val;uint8_t toggle_switch_val;uint8_t foot_switch_val;

uint16_t signal = 0;

uint32_t timer = 0;

int main() {
if (!bcm2835_init()) {printf("bcm2835_init failed. Are you running as root ?");return 1;}
if (!bcm2835_spi_begin()) {printf("bcm2835_spi_begin failed. Are you running as root ?");return 1;}

bcm2835_gpio_fsel(18, BCM2835_GPIO_FSEL_ALT5);bcm2835_gpio_fsel(13, BCM2835_GPIO_FSEL_ALT0);
bcm2835_pwm_set_clock(2);
bcm2835_pwm_set_mode(0, 1, 1);bcm2835_pwm_set_range(0, 64);
bcm2835_pwm_set_mode(1, 1, 1);bcm2835_pwm_set_range(1, 64);

bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);bcm2835_spi_setDataMode(BCM2835_SPI_MODE0);
bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_64);bcm2835_spi_chipSelect(BCM2835_SPI_CS0);
bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0,LOW);
uint8_t mosi[10] = {0x01, 0x00, 0x00};uint8_t miso[10] = {0};

bcm2835_gpio_fsel(PUSH_1, BCM2835_GPIO_FSEL_INPT);bcm2835_gpio_fsel(PUSH_2, BCM2835_GPIO_FSEL_INPT);
bcm2835_gpio_fsel(TOGGLE_SWITCH, BCM2835_GPIO_FSEL_INPT);
bcm2835_gpio_fsel(FOOT_SWITCH, BCM2835_GPIO_FSEL_INPT);
bcm2835_gpio_fsel(LED, BCM2835_GPIO_FSEL_OUTP);

bcm2835_gpio_set_pud(PUSH_1, BCM2835_GPIO_PUD_UP);bcm2835_gpio_set_pud(PUSH_2, BCM2835_GPIO_PUD_UP);
bcm2835_gpio_set_pud(TOGGLE_SWITCH, BCM2835_GPIO_PUD_UP);
bcm2835_gpio_set_pud(FOOT_SWITCH, BCM2835_GPIO_PUD_UP);

fd_set readfds;FD_ZERO(&readfds);struct timeval timeout;timeout.tv_sec = 0;timeout.tv_usec = 0;

char message[30];char* variable;char* value;
"""
    + INITS
    + """
while(1) {
bcm2835_spi_transfernb(mosi, miso, 3);signal = miso[2] + ((miso[1] & 0x0F) << 8);

if (timer == 0) {
timer = 100000;

while(1) { // mabe del this ?
FD_SET(STDIN_FILENO, &readfds);
while (select(1, &readfds, NULL, NULL, &timeout)) {
scanf("%s", message);
variable = strtok(message, "=");
value = strtok(0, "=");
"""
    + VARS
    + """}}

push_1_val = bcm2835_gpio_lev(PUSH_1);push_2_val = bcm2835_gpio_lev(PUSH_2);
toggle_switch_val = bcm2835_gpio_lev(TOGGLE_SWITCH);
foot_switch_val = bcm2835_gpio_lev(FOOT_SWITCH);
bcm2835_gpio_write(LED, !foot_switch_val);
"""
    + TIMER
    + """}
timer--;
"""
    + EFFECTS
    + """
bcm2835_pwm_set_data(1, signal & 0x3F);bcm2835_pwm_set_data(0, signal >> 6);}
bcm2835_spi_end();bcm2835_close();return 0;}
"""
)

if not path.isfile(path.join(curdir, "pedal_pi")):
    if (
        system(
            "gcc "
            + path.join(curdir, "bcm2835.o")
            + " -o "
            + path.join(curdir, "pedal_pi")
            + " -x c -<<EOF"
            + C
            + "EOF"
        )
        != 0
    ):
        raise ChildProcessError("gcc failed to compile")

PEDAL = spawn("sudo " + path.join(curdir, "pedal_pi"), echo=False, encoding="utf-8")

MQTT = Client()
MQTT.username_pw_set("pedal_pi", password="effect[~~~~]")
MQTT.on_message = message
MQTT.connect("localhost")
MQTT.subscribe("pedal_pi")
MQTT.loop_start()

SERVER = HTTPServer(("", 5555), Page)

if not PEDAL.isalive():
    PEDAL.close()
    MQTT.loop_stop()
    raise ChildProcessError("pedal_pi is not running")

print("\nHello !")
print(
    "\nPedal-Pi is running on http://"
    + SERVER.server_address[0]
    + ":"
    + str(SERVER.server_address[1])
)

try:
    SERVER.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down...")
    PEDAL.close()
    MQTT.loop_stop()
    SERVER.shutdown()
    print("\nGood bye !")
