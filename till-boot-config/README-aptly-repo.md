Using aptly to manage a local repository for till boot
------------------------------------------------------

By default, the network booted tills fetch packages to be installed
from the repository at http://www.individualpubs.co.uk/software

This may not be desirable.  If you want to avoid boot-time
dependencies on this repository, a local copy of the repository is
needed.

You can serve this local repository using the same web server that
serves the till configuration file.  Manage the local repository as
the same user that owns the till configuration file, and symlink from
the directory served by the web server to ~/.aptly/public/

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
Version: GnuPG v1.4.11 (GNU/Linux)

mQENBFMGAY8BCAC6h3oq6oK48d8bxMc7jsKKuW/E/ZohmtDaeLsbyIs7+R0oTBPY
Ey9GyzVrBJqnOSzGd0PV9/EGMyXL+JpNMv4H5llemLJkYXFqZJrdpZDcTFJheXUL
8wzCnvBVgC+8mDjstnN3GJW3N3Aa6yo7fBlP4pbmV638dn73jsIk72bmpDKcxD6C
p6dtKBBN32XDSB6qsMtDt9tyUbWr1keQyFbOx2/jhhwyXoGC06jGiIRzj5JWmTh3
cOj6LmIC3aN8GomAwruft7J28WB8zTLSScdLZUnScFBlVRstHmdBy9u8ka/EE6lg
8Pj+1MbWWeOTmbm8fBNQHYYwnEh5d5JE7UlBABEBAAG0QVN0ZXBoZW4gRWFybHkg
KFJlcG9zaXRvcnkgc2lnbmluZyBrZXkpIDxzZGVAaW5kaXZpZHVhbHB1YnMuY28u
dWs+iQE+BBMBAgAoBQJTBgGPAhsDBQkSzAMABgsJCAcDAgYVCAIJCgsEFgIDAQIe
AQIXgAAKCRBpTB4MZXuk8kM7B/4uRGpObtYFPjm/yXcJZvaFE6HhJLC8rdyR/Mp9
mUtj60PjZdFc/CLDOwth/MiBga6r8UPl6h5Nnh/dyjYRs9tVDzCZOtXDy0hgl2C2
LvGkREXUbC7+tNFkw8mGEHeCgYEKncBwaADLgKLY3KC2KSZKopTs46YFsOhmDBwC
XVzN6Vy7qtWA5lfb82ju9ywbaGb7/Yff43oFY19J+PpgrKrzDUauaZg++bKt1nA3
THy6gn7QIkfSmI8+Wr87/WjfKbmsLKiYeCHR40c9UPUNNpXNrexQGdIGAJsRMgKx
CFpI8sgLtA6KH6kTAr4vvc5qk0pOGo4y4iQOMPn6JtT1uc9l
=YqGZ
-----END PGP PUBLIC KEY BLOCK-----
EOF
```

Optionally create a key to sign the local repository.  This isn't
strictly necessary: the network booted tills have to trust their boot
server anyway, and will typically be booting over a private network.


In the rest of the document, replace 'bionic-tills' with whatever
distribution you are setting up for.

Tell aptly about the main repository (filtering out the 'till-boot-*'
packages which are large and unnecessary on a network-booted till
client):

```
aptly mirror create \
  -filter='!Name (~ till-boot-.*)' \
  bionic-tills http://www.individualpubs.co.uk/software bionic-tills main
```

Create a local repository to hold the packages being loaded by the
tills:

```
aptly repo create bionic-tills
```

Publish the repository:

```
aptly publish repo \
  -distribution=bionic-tills \
  -architectures=i386,amd64 \
  -skip-signing \
  bionic-tills
```

(If you want to sign the published repository, see the relevant
options at (the aptly documentation page for aptly publish repo)[https://www.aptly.info/doc/aptly/publish/repo/].)


Updating the repository
=======================

To update packages in the local repository, first update the mirror,
then import updated packages into the repository, finally publish the
repository.

```
aptly mirror update bionic-tills
aptly repo import bionic-tills bionic-tills package1 package2 ...
aptly publish update --skip-signing bionic-tills
```

aptly doesn't delete package files by default when they are
superceded.  You can do this using:

```
aptly db cleanup
```
