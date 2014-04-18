#!/usr/bin/python

CHANGELOG = """%(debian_name)s (%(version)s-1) unstable; urgency=low

  * Initial release (Closes: #nnnn)

 -- %(debian_author)s  %(date)s

"""

CONTROL = """Source: %(Source)s
Section: web
Priority: extra
Maintainer: Debian Javascript Maintainers <pkg-javascript-devel@lists.alioth.debian.org>
Uploaders: %(Uploaders)s
Build-Depends:
 debhelper (>= %(debhelper)s)
 , dh-buildinfo
 , nodejs
Standards-Version: %(Standards-Version)s
Homepage: %(Homepage)s
Vcs-Git: %(Vcs-Git)s
Vcs-Browser: %(Vcs-Browser)s

Package: %(Package)s
Architecture: all
Depends:
 ${misc:Depends}
 , %(Depends)s
Description: %(Description)s
 %(Description_Long)s
 .
 Node.js is an event-based server-side JavaScript engine.
"""

RULES = """#!/usr/bin/make -f
# -*- makefile -*-

# Uncomment this to turn on verbose mode.
#export DH_VERBOSE=1

%%:
	dh $@

#override_dh_auto_build:

#override_dh_auto_test:

%(overrides)s

"""

COPYRIGHT = """Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: %(upstream_name)s
Source: %(source)s

Files: *
Copyright: %(upstream_date)s %(upstream_author)s
License: %(upstream_license_name)s

License: %(upstream_license)s

Files: debian/*
Copyright: %(debian_date)s %(debian_author)s
License: %(debian_license_name)s

License: %(debian_license)s
"""

WNPP = """Subject: ITP: %(debian_name)s -- %(description)s
Package: wnpp
Severity: wishlist
Owner: %(debian_author)s

* Package name    : %(debian_name)s
  Version         : %(version)s
  Upstream Author : %(upstream_author)s
* URL             : %(homepage)s
* License         : %(license)s
  Programming Lang: JavaScript
  Description     : %(description)s

 FIX_ME bug long description
 .
 Node.js is an event-based server-side JavaScript engine.

"""

LICENSES = {}

LICENSES['GPL-2'] = """GPL-2
 This package is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>
 .
 On Debian systems, the complete text of the GNU General
 Public License version 2 can be found in "/usr/share/common-licenses/GPL-2".
"""

LICENSES['GPL-3'] = """GPL-3
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 .
 On Debian systems, the complete text of the GNU General
 Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
"""

LICENSES['Apache'] = """Apache-2.0
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 .
 http://www.apache.org/licenses/LICENSE-2.0
 .
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 .
 On Debian systems, the complete text of the Apache version 2.0 license
 can be found in "/usr/share/common-licenses/Apache-2.0".
"""

LICENSES['Artistic'] = """Artistic-1.0
 This program is free software; you can redistribute it and/or modify it
 under the terms of the "Artistic License" which comes with Debian.
 .
 THIS PACKAGE IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED
 WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES
 OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
 .
 On Debian systems, the complete text of the Artistic License
 can be found in "/usr/share/common-licenses/Artistic".
"""

LICENSES['BSD'] = """BSD-3-Clause
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. Neither the name of the University nor the names of its contributors
    may be used to endorse or promote products derived from this software
    without specific prior written permission.
 .
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE HOLDERS OR
 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 .
 On Debian systems, the complete text of the BSD License
 can be found in "/usr/share/common-licenses/BSD".
"""

LICENSES['LGPL-2'] = """LGPL-2
 This package is free software; you can redistribute it and/or
 modify it under the terms of the GNU Lesser General Public
 License as published by the Free Software Foundation; either
 version 2 of the License, or (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Lesser General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 .
 On Debian systems, the complete text of the GNU Lesser General
 Public License can be found in "/usr/share/common-licenses/LGPL-2".
"""

LICENSES['LGPL-3'] = """LGPL-3
 This package is free software; you can redistribute it and/or
 modify it under the terms of the GNU Lesser General Public
 License as published by the Free Software Foundation; either
 version 3 of the License, or (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Lesser General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 .
 On Debian systems, the complete text of the GNU Lesser General
 Public License can be found in "/usr/share/common-licenses/LGPL-3".
"""

LICENSES['MIT'] = """MIT
 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

LICENSES['Expat'] = """Expat
 Permission is hereby granted, free of charge, to any person
 obtaining a copy of this software and associated documentation files
 (the "Software"), to deal in the Software without restriction,
 including without limitation the rights to use, copy, modify, merge,
 publish, distribute, sublicense, and/or sell copies of the Software,
 and to permit persons to whom the Software is furnished to do so,
 subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
"""

WATCH_GITHUB = """version=3
opts=filenamemangle=s/.*\/v?([\d\.-]+)\.tar\.gz/%(debian_name)s-$1.tar.gz/ \\
 %(homepage)s/tags .*/archive/v?([\d\.]+).tar.gz
"""
