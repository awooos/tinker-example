#include <hal.h>
#include "display.h"

void hal_print(const char *string)
{
    vga_print(string);
    uart_print(string);
}

void hal_init()
{
    //
}
