#include <hal.h>
#include "display.h"

int hal_putchar(int c) {
    // TODO: If vga_putchar() or uart_putchar() return EOF, return EOF from here.
    vga_putchar(c);
    uart_putchar(c);

    return c;
}

void hal_print(const char *string)
{
    vga_print(string);
    uart_print(string);
}

void hal_init()
{
    //
}
