## 0.2.0 (2014-07-04)

 * [new] - only python3 is now supported
 * [new] - use wnpp-check instead of external service wnpp.debian.net
 * [new] - add support to autopkgtest - make a simple module require check
 * [new] - on create add option --upstream-homepage
 * [new] - on create add option --upstream-author
 * [new] - forward ITP to debian-devel@lists.debian.org

 * [fix] - correctly set filenamemangle for fakeupstream.cgi
 * [fix] - correctly localized module location and node_modules path
 * [fix] - don't expose extenal modules while import Npm2Deb
 * [fix] - update dversionmangle according with uscan wiki page
 * [fix] - support repositories defined as str in package.json
 * [fix] - check if module version is valid before parse it - closes #10
 * [fix] - check if readmeFilename is not a emtpy value in json before use it


## 0.1.3 (2014-06-04)
 * [new] - set email headers in ITP template
 * [fix] - fallback on qa.debian.org/fakeupstream.cgi when uscan fail

## 0.1.2 (2014-05-12)
 * [new] - add a dversionmangle option to watch by default
 * [fix] - get builddeps required by the correct version of the module
 * [fix] - catch KeyboardInterrupt - fail nicely if contrl+c detected

## 0.1.1 (2014-05-07)
 * [fix] - prevent infinite loop looking for reverse dependencies
 * [fix] - lintian warning about bsd licenses
 * [fix] - PEP-8 compliance

## 0.1.0
 * Initial release
