/**
  * @file ${obj.name.lower()}.h
  * @author generated by mrt-device.py
  * @brief register defintions for ${obj.name} device
  *
  */

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdint.h>
#include <stdbool.h>
#include "Devices/RegDevice/register_device.h"
#include "${obj.name.lower()}_regs.h"

/*user-block-top-start*/
/*user-block-top-end*/


/*******************************************************************************
  Sruct                                                                                
*******************************************************************************/

typedef struct{
    mrt_regdev_t mRegDev; //ptr to register base device 
    % for key,reg in obj.regs.items():
    mrt_reg_t ${"m" + obj.camelCase(reg.name)};  //${reg.desc}
% endfor
/*user-block-struct-start*/
/*user-block-struct-end*/
}${obj.name.lower()}_t;

% if "I2C" in obj.bus.upper():
/**
 * @brief initializes ${obj.name} device for i2c bus
 * @param dev ptr to ${obj.name} device
 * @param i2c handle for i2c bus
 */
mrt_status_t ${obj.prefix.lower()}_init_i2c(${obj.name.lower()}_t* dev, mrt_i2c_handle_t i2c);
% endif
% if "SPI" in obj.bus.upper():
/**
 * @brief initializes ${obj.name} device for i2c bus
 * @param dev ptr to ${obj.name} device
 * @param spi handle for i2c bus
 */
mrt_status_t ${obj.prefix.lower()}_init_spi(${obj.name.lower()}_t* dev, mrt_spi_handle_t spi, mrt_gpio_t chipSelect );
% endif

/**
  *@brief tests interface with device
  *@param dev ptr to ${obj.name} device
  *@return MRT_STATUS_OK if test is passed 
  *@return MRT_STATUS_ERROR if test fails
  */
mrt_status_t ${obj.prefix.lower()}_test(${obj.name.lower()}_t* dev);

/**
  *@brief writes register of device
  *@param dev ptr to ${obj.name} device
  *@param reg ptr to register definition
  *@param data data to be write
  *@return status (type defined by platform)
  */
#define ${obj.prefix.lower() +"_write_reg"}(dev, reg, data) regdev_write_reg(&(dev)->mRegDev, (reg), (data))

/**
  *@brief reads register of device
  *@param dev ptr to ${obj.name} device
  *@param reg ptr to register definition
  *@param data ptr to store data
  *@return value of register
  */
#define ${obj.prefix.lower() +"_read_reg"}(dev, reg) regdev_read_reg(&(dev)->mRegDev, (reg))


/*user-block-bottom-start*/
/*user-block-bottom-end*/

#ifdef __cplusplus
}
#endif
