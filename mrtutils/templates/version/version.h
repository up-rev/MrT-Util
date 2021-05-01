/**
 * @file version.h
 * @author generated by mrt-version (https://github.com/uprev-mrt/mrtutils)
 * @brief version header
 * @date ${t.getDate()}
 */

#define ${obj.prefix.upper()}VERSION_MAJOR      ${obj.major}
#define ${obj.prefix.upper()}VERSION_MINOR      ${obj.minor}
#define ${obj.prefix.upper()}VERSION_PATCH      ${obj.patch} 
#define ${obj.prefix.upper()}VERSION_BUILD      ${obj.build} 
#define ${obj.prefix.upper()}VERSION_BRANCH     "${obj.branch}"
#define ${obj.prefix.upper()}VERSION_COMMIT     "${obj.hash}"

#define ${obj.prefix.upper()}VERSION_STRING "${obj.major}.${obj.minor}.${obj.patch}.${obj.build}"

