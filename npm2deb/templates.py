CHANGELOG = """%(debian_name)s (%(version)s-1) UNRELEASED; urgency=medium

  * Initial release (Closes: #nnnn)

 -- %(debian_author)s  %(date)s
"""

description_template = """ Write the short and long descriptions for the Debian package as
 explained in the Developer's Reference, §6.2.1 – §6.2.3.
 .
 You can start with the short upstream package description,
 “%(upstream_description)s”.
 .
 Be aware that most upstream package descriptions are not written to
 conform with Debian package guidelines. You need to explain the role
 of this package for a Debian audience.
"""

CONTROL = """Source: %(Source)s
Section: javascript
Priority: optional
Maintainer: Debian Javascript Maintainers <pkg-javascript-devel@lists.alioth.debian.org>
Uploaders: %(Uploaders)s
Testsuite: autopkgtest-pkg-nodejs
Build-Depends:
 debhelper-compat (= %(debhelper)s)
 , nodejs (>= 6)
 , pkg-js-tools (>= 0.8.10)
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
""" + description_template

RULES = """#!/usr/bin/make -f
# -*- makefile -*-

# Uncomment this to turn on verbose mode.
#export DH_VERBOSE=1

%%:
	dh $@ --with nodejs

#override_dh_auto_build:

%(overrides)s"""

COPYRIGHT = """Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: %(upstream_name)s
Upstream-Contact: %(upstream_contact)s
Source: %(source)s

Files: *
Copyright: %(upstream_date)s, %(upstream_author)s
License: %(upstream_license_name)s
%(upstream_license)s
Files: debian/*
Copyright: %(debian_date)s, %(debian_author)s
License: %(debian_license_name)s

%(debian_license)s"""

WNPP = """To: submit@bugs.debian.org
Subject: ITP: %(debian_name)s -- %(description)s

Package: wnpp
Severity: wishlist
Owner: %(debian_author)s
X-Debbugs-CC: debian-devel@lists.debian.org

* Package name    : %(debian_name)s
  Version         : %(version)s
  Upstream Author : %(upstream_author)s
* URL             : %(homepage)s
* License         : %(license)s
  Programming Lang: JavaScript
  Description     : %(description)s

 FIX_ME: This ITP report is not ready for submission, until you are
 confident this package description is ready for Debian.
 .
""" + description_template + """
FIX_ME: Explain why this package is suitable for adding to Debian. Is
it a dependency of some other package? What benefit does it provide
compared to other similar packages already in Debian?

FIX_ME: Explain how you intend to consistently maintain this package
in Debian. If you are not yet a Debian member, does this package need
a sponsor? Do you have co-maintainers? Are you a member of the Debian
JavaScript maintainers team?
"""

LICENSES = {}

LICENSES['GPL-2'] = """GPL-2+
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

LICENSES['GPL-3'] = """GPL-3+
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

LICENSES['BSD-2-clause'] = """%(name)s
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
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
"""

LICENSES['BSD-3-clause'] = """%(name)s
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
"""

LICENSES['BSD-4-clause'] = """%(name)s
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
 4. Neither the name of the organization nor the names of its contributors
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

LICENSES['MIT'] = LICENSES['Expat']

LICENSES['ISC'] = """ISC
 Permission to use, copy, modify, and/or distribute this software for any
 purpose with or without fee is hereby granted, provided that the above
 copyright notice and this permission notice appear in all copies.
 .
 THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

WATCH = {}

WATCH['github'] = """version=4
opts=\\
dversionmangle=%(dversionmangle)s,\\
filenamemangle=s/.+\/v?(\d\S+)\.tar\.gz/%(modulename)s-$1\.tar\.gz/ \\
 %(url)s/tags .*/v?(\d\S+)\.tar\.gz
"""

WATCH['gitlab'] = """version=4
opts=\\
dversionmangle=%(dversionmangle)s \\
 %(url)s/tags?sort=updated_desc .*/archive/.*?v?([\d\.]+)\.tar\.gz
"""

WATCH['npmregistry'] = """version=4
# It is not recommended use npmregistry. Please investigate more.
# Origin url: %(url)s
# Take a look at https://wiki.debian.org/debian/watch/
opts="searchmode=plain,pgpmode=none" \\
 https://registry.npmjs.org/%(module)s \\
 https://registry.npmjs.org/%(remodule)s/-/%(modulename)s-(\d[\d\.]*)@ARCHIVE_EXT@
"""

METADATA = {}

METADATA['github'] = """---
Archive: GitHub
Bug-Database: %(url)s/issues
Contact: %(url)s/issues
Name: %(module)s
Repository: %(url)s.git
Repository-Browse: %(url)s
"""

METADATA['gitlab'] = """---
Archive: GitLab
Bug-Database: %(url)s/issues
Contact: %(url)s/issues
Name: %(module)s
Repository: %(url)s.git
Repository-Browse: %(url)s
"""

GBPCONF = """[DEFAULT]
pristine-tar = True
filter = [ '.gitignore', '.travis.yml', '.git*' ]
"""
