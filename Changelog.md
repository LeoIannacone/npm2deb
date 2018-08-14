## 0.2.8 (2018-08-15)
 * [fix] Exclude unwanted files from debian/install
 * [new] Move primary search from alioth to salsa - closes #106
 * [new] Support scopes, ie, '@<scope>/' in module names
 * [new] Use latest standards version
 * [new] Support packaging of specific version of a module

## 0.2.7 (2017-07-19)
 * [new] Add all files and directories in tarball to debian/install
 * [new] Support regex in package mapper
 * [new] Abort execution in non-utf environments
 * [fix] Use debian-name for repository and bug search
 * [fix] Handle non-standard tarball root directory names
 * [new] Improved package search
	 search packages in all debian suites with rmadison
 * [new] Updated description templates
 * [new] Use npmjs page as homepage fallback
 * [fix] Handle arrays in man field

## 0.2.6 (2016-11-10)
 * [fix] use rmadison to find available packages
 * [fix] convert package name to lowercase
 * [fix] handle invalid repository field
 * [fix] bump standards version to 3.9.8
 * [fix] converting dependency packages version format
 * [fix] for npm install overhead
 * [new] automating uscan, uupdate, dpkg-buildpackage

## 0.2.2 (2014-10-10)
 * [fix] bump Standards-Version to 3.9.6

## 0.2.1 (2014-08-23)
 * [new] add support to ISC and to other BSD licenses - closes #9
 * [fix] add URL to licence-specification if license not supported
 * [fix] hard link MIT license to Expat
 * [fix] set UNRELEASED in debian/changelog - closes #12

## 0.2.0 (2014-07-04)
 * [new] only python3 is now supported
 * [new] use wnpp-check instead of external service wnpp.debian.net
 * [new] add support to autopkgtest - make a simple module require check
 * [new] on create add option --upstream-homepage
 * [new] on create add option --upstream-author
 * [new] forward ITP to debian-devel@lists.debian.org

 * [fix] correctly set filenamemangle for fakeupstream.cgi
 * [fix] correctly localized module location and node_modules path
 * [fix] don't expose extenal modules while import Npm2Deb
 * [fix] update dversionmangle according with uscan wiki page
 * [fix] support repositories defined as str in package.json
 * [fix] check if module version is valid before parse it - closes #10
 * [fix] check if readmeFilename is not a emtpy value in json before use it


## 0.1.3 (2014-06-04)
 * [new] set email headers in ITP template
 * [fix] fallback on qa.debian.org/fakeupstream.cgi when uscan fail

## 0.1.2 (2014-05-12)
 * [new] add a dversionmangle option to watch by default
 * [fix] get builddeps required by the correct version of the module
 * [fix] catch KeyboardInterrupt - fail nicely if contrl+c detected

## 0.1.1 (2014-05-07)
 * [fix] prevent infinite loop looking for reverse dependencies
 * [fix] lintian warning about bsd licenses
 * [fix] PEP-8 compliance

## 0.1.0
 * Initial release
