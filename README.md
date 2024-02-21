# Network booting of tills

This repository contains scripts used to generate Debian packages for
network booting of tills and information screens.

These packages are installed on a server (usually, but not
necessarily, the main till).

You must be (real) root when running the image build scripts.

Required packages:

```
debootstrap squashfs-tools systemd-container qemu-user-static binfmt-support wget parallel debhelper debian-archive-keyring
```

To build the boot image and loaders package, as root:

```
./build-all
```

To build the till-boot-config package:

```
cd till-boot-config
dpkg-buildpackage -us -uc
```

You can build the boot image packages on a machine of any architecture
(eg. amd64 on arm64 or armhf on i386), but building will be fastest
when a boot image is built on a machine with compatible
architecture. If you have access to both a PC and a Raspberry you may
want to split the work between the two for speed. Edit the build-all
script appropriately.


## Terms used

"platform": the type of computer to be booted.  Platforms vary in
their requirements for boot files and their placement: for example,
the 'pc' platform uses ipxe, boot-time config is placed into
'hostname.ipxe' files, and the DHCP server points the client at the
appropriate file.  The 'rpi' platform uses the PI's own network
bootloader; boot-time config and supporting files are placed into a
subdirectory named according to the serial number of the PI to be
booted.

Current platforms are 'pc' and 'rpi'.

"distribution": the codename of the debian-derived operating system,
eg. 'xenial', 'bionic', 'focal' for Ubuntu, 'buster' or 'bullseye' for
debian or raspberry pi os


## Currently working

(But see bug list at end.)

* pc bookworm {i386,amd64}
* rpi bookworm {armhf,arm64}

bullseye could be made to work again with additional scripts to choose
between wayfire and X


# How platforms boot

## PC

For "legacy" boot: The PXE bootloader in ROM obtains an IP address,
TFTP server address and the boot filename "ipxe.pxe" from the DHCP
server, and loads `ipxe.pxe` via TFTP. (If the PXE bootloader in ROM
_is_ [iPXE](https://ipxe.org/), this step is skipped.)

For UEFI boot: The PXE bootloader in ROM obtains an IP address, TFTP
server address and the boot filename "ipxe.efi" from the DHCP server,
and loads `ipxe.efi` via TFTP.

[iPXE](https://ipxe.org/) performs DHCP again, but this time is given
a HTTP URL as the boot filename, pointing to the `.ipxe` configuration
file specific to the till being booted.

iPXE loads the `{hostname}.ipxe` file via HTTP. This file instructs it
to fetch the kernel and initrd via HTTP, and then start the kernel. If
iPXE doesn't have Linux support built-in (for example if it's a small
build of it in ROM on a legacy boot system) it chainloads the
fully-featured `ipxe.pxe` instead and starts again.

The kernel runs the initrd, which performs DHCP to obtain an IP
address, and NFS mounts the till boot image from the location
specified on the kernel command line in the `{hostname}.ipxe`
file. The squashfs image is loopback mounted, and an overlayfs is
created to enable ramdisk-backed write to the image. The image is then
started with the overlayfs as the root filesystem.

## Raspberry Pi

The boot ROM in the Pi performs DHCP to obtain an IP address and TFTP
server address. On Pis prior to Pi 4, it loads "bootcode.bin" via TFTP
and then starts again.

The Pi loads a number of files from "{serialnumber}/" via TFTP:
`config.txt`, `start.elf` or `start4.elf`, etc. and ultimately loads a
kernel, initrd, and `cmdline.txt`.

The kernel runs the initrd, which performs DHCP to obtain an IP
address, and NFS mounts the till boot image from the location
specified on the kernel command line in the `cmdline.txt` file. The
squashfs image is loopback mounted, and an overlayfs is created to
enable ramdisk-backed write to the image. The image is then started
with the overlayfs as the root filesystem.

# TODO / bugs for bookworm

wayfire plugin to call seat::cursor::set_touchscreen_mode(true) on
init?  (There's a "hide_cursor" plugin in wayfire-plugins-extra —
maybe compile and package that and include it in the image? See
https://github.com/seffs/wayfire-plugins-extra-raspbian )

Fonts look a bit off — the baseline for the proportional font appears
to be too high compared to the monospace font. This doesn't happen on
bullseye. Entirely possible it's a bug in quicktill,
though. Workaround: added a pitch adjustment command line parameter.

Need a way for quicktill to unblank the screen on receiving a
usertoken. Some way for it to speak Wayland idle protocol?
