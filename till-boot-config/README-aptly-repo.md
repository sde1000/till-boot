Using aptly to manage a local repository for till boot
------------------------------------------------------

The network booted tills can be configured to fetch packages from any
repository at boot time.  For resilience, it may be desirable to
configure a local till software repository to avoid boot-time
dependencies on remote repositories.

You can serve this local repository using the same web server that
serves the till configuration file.  Manage the local repository as
the same user that owns the till configuration file, and symlink from
the directory served by the web server to `~/.aptly/public/`

Initial setup
=============

Make sure aptly is installed:

```
sudo apt-get install aptly
```

Import the signing key for the main repository:

```
gpg --no-default-keyring --keyring trustedkeys.gpg --import <<EOF
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQGNBF+1RAABDADf1ShTPOBMZCocpniMNTgBkEoktMrQTp6m6cTx+jyfl8Tt7/k3
PE1mOeFF5a6Cfkz5xIbE/05x8V9+ix2qOj3Z/g6WpHBhCWEkB6Sfx2s8G5rSGJin
ip2MO3ieYpwbrRVT5BkL12zb4+mZ45UqywrRBoJGii60jcFQu/cG0qAC6pRsxgXg
IPSo1wqgl6RAr6Q/6j4wDv/B0EOPkxexjLP08SHbGBIbaqkMyGinC9ztWt2HnLu6
pTJDfSXX1zxv88rABEp9n2P99oo7h476AbG6TGmkSqCDRzcFV0ELpUvZ7eV1SNRH
eSW74QcKuJXx+SWnbb7gVKWlnhxvWOhCoE0U1/iCUnbDimS/wmyBPmMRq/tlfuW4
ANeHaneo02QFpSlSN4LctHOnh0pur/v0TUnfzyyybUSw0+j/E8tIcINOJAd4Q5Ca
zoIFtwuNUbsaGarkPoifL+IZfymDVwCMdoU1y+VZ/OdJ8tXNv+K4749M4TAQh4Nz
gtLFXclvdTnh9G0AEQEAAbQ4UXVpY2t0aWxsIHJlcG9zaXRvcnkgc2lnbmluZyBr
ZXkgPHN0ZXZlQGFzc29ydGVkLm9yZy51az6JAdQEEwEKAD4WIQTKFvDXC5y5b3+W
R502+MldnVZUvgUCX7VEAAIbAwUJEswDAAULCQgHAwUVCgkICwUWAwIBAAIeAQIX
gAAKCRA2+MldnVZUvgbfC/wN/Y2+6dvFxIGSbjJka3/jkXdckGjvmYabZMNeSD2a
C5lV5MLfDj5QsGVTznNNR7YuwZJswRK2LJEUsEzs9v7lFRxyVbYRb8nZviv3SqAV
adyimApnmJXFxM8CbvMYHTvnJXWiLts3Xiktg0zi48AN9ZQb4EfCclqNbJzt6HNJ
hBsyr1UzJfzZMob6T35v/eS6GczdoyTlg4ff4QQtoaHmsdG/pO4W9bYbpLKfieLv
vEzeKo8f2bqgFgA6TJo0yPC+CgLoBpTDyoclhagTwWu0Jseb3cehTuUIkRh0qNl2
dy63W4nfwjuubfgs58s/zsLu79Dw3bU29lF9bv6CUHuC1khRHEbTenoSKVCANrWu
eR8RUEopAqrAel9TlPVpOc2ZqVlliNg3WgNbHusRJP/lodJn5a6E/wDg75OCaFUN
4PXIn5t1xUFyRMUxtPcGioS3nA+Xa5nEJZKztjIhG+4USKh15qhEn+PvrJD4iOPu
s7K9z0AlSZTF80D8a7HE5k4=
=WsZn
-----END PGP PUBLIC KEY BLOCK-----
EOF
```

NB if you previously imported the key under Ubuntu 18.04, delete
`~/.gnupg/trustedkeys.gpg` and import again; there was a bug in gnupg in
Ubuntu 18.04 that corrupted the key on import leading to error
messages like `gpgv: keydb_search failed: invalid packet` under Ubuntu
20.04.

Tell aptly about the main repository (filtering out the 'till-boot-*'
packages which are large and unnecessary on a network-booted till
client):

```
aptly mirror create \
  -filter='!Name (~ till-boot-.*)' \
  upstream-tills http://quicktill.assorted.org.uk/software tills main
```

Create a local repository to hold the packages being loaded by the
tills:

```
aptly repo create tills
```

Publish the repository:

```
aptly publish repo \
  -distribution=tills \
  -architectures=i386,amd64,armhf,arm64 \
  -skip-signing \
  tills
```

(If you want to sign the published repository, see the relevant
options at [the aptly documentation page for aptly publish repo](https://www.aptly.info/doc/aptly/publish/repo/).)


Updating the repository
=======================

To update packages in the local repository, first update the mirror,
then import updated packages into the repository, finally publish the
repository.

```
aptly mirror update upstream-tills
aptly repo import upstream-tills tills package1 package2 ...
aptly publish update --skip-signing tills
```

aptly doesn't delete package files by default when they are
superceded.  You can do this using:

```
aptly db cleanup
```


Using the repository
====================

aptly will put the local repository in `~/.aptly/public` — you should
arrange for this to be served by the till configweb server.  Eg:

```
cd configweb
ln -s ~/.aptly/public software
```

You can then add this to the till-boot config:

```
  repos:
   - "deb [trusted=yes] http://192.168.73.30/software tills main"
```
