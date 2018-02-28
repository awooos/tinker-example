#include <hal.h>
#include <dmm.h>
#include <ali.h>
#include <flail.h>

void tinker_kernel_main()
{
    hal_init();
    dmm_init();
    ali_init(&dmm_malloc, &dmm_free, &dmm_realloc);
    flail_init("tinker-generated kernel", &kprint);

}