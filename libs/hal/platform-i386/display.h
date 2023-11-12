#ifndef HAL_MAIN_H
#define HAL_MAIN_H

int vga_putchar(int c);
int uart_putchar(int c);
int hal_putchar(int c);

void vga_print(const char *string);
void uart_print(const char *string);
void hal_print(const char *string);

#endif
