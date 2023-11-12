#include <flail.h>
#include <dmm.h>
#include <ali.h>
#include <tinker.h>
#include <hal.h>

void tinker_kernel_main(void)
{
    flail_init("tinker-generated kernel", &hal_putchar);
    dmm_init(&_flail_panic);
    ali_init(&dmm_malloc_, &dmm_free_, &dmm_realloc_);

    hal_init();

}
