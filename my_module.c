#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/string.h>
#include <linux/stat.h>

 // #define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#define MAX_STR_SIZE 64

static int idx = 0;
static unsigned char ch_val = 'A';
static char my_str[MAX_STR_SIZE] = "Default string";

/* my_str function */

static void my_str_update(void)
{
    my_str[idx] = ch_val;
}

static int my_str_get(char *buf, const struct kernel_param *kp)
{
    return sprintf(buf, "%s \n", my_str);
}

static const struct kernel_param_ops my_str_param_ops = {
    .get = my_str_get,
};

module_param_cb(my_str, &my_str_param_ops, NULL, 0444);
MODULE_PARM_DESC(my_str, "String value (max 63 characters)");

/* my_str function end*/

/* ch_val function */

static int ch_val_set(const char *val, const struct kernel_param *kp)
{
    unsigned long tmp;
    int ret;

    ret = kstrtoul(val, 10, &tmp);
    if (ret)
        return ret;
    if (tmp > 255) {
        pr_warn("ch_val %lu out of range (0-255)\n", tmp);
        return -EINVAL;
    }
    ch_val = (unsigned char)tmp;

    pr_info("ch_val value = %c (%d)\n", ch_val, ch_val);
    my_str_update();
    return 0;
}

static int ch_val_get(char *buf, const struct kernel_param *kp)
{
    return sprintf(buf, "%c (%d) \n", ch_val, ch_val);
}

static const struct kernel_param_ops ch_val_params_ops = {
    .set = ch_val_set,
    .get = ch_val_get,
};

module_param_cb(ch_val, &ch_val_params_ops, &ch_val, 0664);
MODULE_PARM_DESC(ch_val, "Character value (0-255)");

/* ch_val function end*/

/* idx function */

static int idx_set(const char *val, const struct kernel_param *kp)
{
    int ret;
    unsigned long tmp;
    ret = kstrtoul(val, 10, &tmp);
    if(ret)
        return ret;
    if (tmp > 64)
    {
        pr_warn("швч %lu out of range (0-63)\n", tmp);
        return -EINVAL;
    }
    
    idx = (int)tmp;
    pr_info("idx value = %d \n", idx);
    return 0;
}

static int idx_get(char *buf, const struct kernel_param *kp)
{
    return sprintf(buf, "%d \n", idx);
}

static const struct kernel_param_ops idx_param_ops = {
    .set = idx_set,
    .get = idx_get,
};

module_param_cb(idx, &idx_param_ops, &idx, 0664);
MODULE_PARM_DESC(idx, "Index of position in my_str (0-63)");

/* idx function end*/

static int __init hello_init(void)
{
    pr_info("hello, from kernel \n");
    pr_info("Initial: idx=%d, ch_val='%c'(%d), my_str=%s\n", 
           idx, ch_val, ch_val, my_str);
    return 0;
}

static void __exit hello_exit(void)
{
    pr_info("bye, from kernel \n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Vladislav Akhmedov");
MODULE_DESCRIPTION("Kernel module with configurable parameters using permission macros");