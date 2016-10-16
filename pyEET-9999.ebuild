# Copyright 1999-2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-x86/dev-python/simplejson/simplejson-3.6.4.ebuild,v 1.8 2014/12/04 08:48:37 ago Exp $

EAPI=6
PYTHON_COMPAT=( python{2_7,3_3,3_4} pypy )

inherit distutils-r1 git-r3

DESCRIPTION="Python client for EET"
HOMEPAGE="https://github.com/v154c1/pyEET/"
SRC_URI=""

LICENSE="BSD"
SLOT="0"
KEYWORDS="~amd64 ~arm ~x86"

DEPEND="dev-python/setuptools[${PYTHON_USEDEP}]"

RDEPEND="dev-python/pyopenssl
	dev-python/lxml
	dev-python/requests
	dev-python/pytz"

DOCS=( README.md LICENSE )

EGIT_REPO_URI="https://github.com/v154c1/pyEET.git"
