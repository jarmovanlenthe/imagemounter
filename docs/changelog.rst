Release notes
=============

2.0.2 (2015-06-17)
------------------
* Bugfix in --check regarding the python-magic module
* Fix vmware-mount support

2.0.1 (2015-06-17)
------------------
* Changed the default ``fsfallback`` to ``unknown``, instead of ``none``.

2.0 (2015-06-17)
----------------
* Introduce support for XFS, ISO, JFFS2, FAT, SquashFS, CramFS, VMFS, UDF and Minix (cheers martinvw!)
* Add ability to read the disk GUID using disktype, and read the filesystem magic for better detection of filesystems (cheers martinvw!)
* Add support for 'mounting' directories and compressed files using avfs (cheers martinvw!)
* Add support for detecting volumes using parted
* Introduce facility to carve filesystems for removed files, even in unallocated spaces
* Add --no-interaction for scripted access to the CLI
* Add --check for access to an overview of all dependencies of imagemounter
* Add --casename (and corresponding Python argument) to easily recognize and organize multiple mounts on the same system
* Change --clean to --unmount, supporting arguments such as --mountdir and --pretty, and made the code more robust and easier to read and extend
* Detect terminal color support and show color by default

* BSD is now called UFS
* --stats is now the default in the Python script
* NTFS mount now also shows the system files by default
* Do not stop when not running as root, but warn and probably fail miserably later on
* fstype now stores the detected file system type, instead of the fstype as determined by fill_stats
* Logging now properly uses the Python logging framework, and there are now 4 verbosity levels
* Changes to how the pretty names are formatted
* Some Py2/Py3 compatibility fixes

1.5.3 (2015-04-08)
------------------
* Add support for ``vmware-mount``

1.5.2 (2015-04-08)
------------------
* Ensure volume.size is always int
* Fixed a GPT/DOS bug caused by TSK
* Add FAT support

1.5.1 (2014-05-22)
------------------
* Add disk index for multi-disk mounts

1.5.0 (2014-05-14)
------------------
* Add support for volume detection using mmls
* Python 3 support
* Bugfix in luksOpen

1.4.3 (2014-04-26)
------------------
* Experimental LUKS support

1.4.2 (2014-04-26)
------------------
* Bugfix that would prevent proper unmounting

1.4.1 (2014-02-10)
------------------
* Initial Py3K support
* Included script is now called imount instead of mount_images

1.4.0 (2014-02-03)
------------------
* Disk is now a seperate class
* Some huge refactoring
* Numerous bugfixes, including resolving issues with unmounting
* Rename image_mounter to imagemounter
* Remove mount_images alias

1.3.1 (2014-01-23)
------------------
* More verbosity with respect to failing mounts

1.3.0 (2014-01-23)
------------------
* Add support for single volume mounts
* Add support for dummy base mounting
* Add support for RAID detection and mounting

1.2.9 (2014-01-21)
------------------
* Improve support for some types of disk images
* Some changes in the way some command-line arguments work (removed -vs, -fs and -fsf)

1.2.8 (2014-01-08)
------------------
* Make --stats the default
* Print the volume size and offset in verbose mode in the CLI
* Add imount as command line utility name

1.2.7 (2014-01-08)
------------------
* Add --keep

1.2.6 (2014-01-08)
------------------
* Use fallback commands for base image mounting if the normal one fails
* Add multifile option to Volume to control whether multifile argument passing should be attempted
* Fix error in backwards compatibility of mount_partitions
* Copy the label of a volume to the last mountpoint if it looks like a mountpoint

1.2.5 (2014-01-07)
------------------
* Ability to automatically detect the mountpoint based on files in the filesystem

1.2.4 (2013-12-16)
------------------
* Partition is now Volume
* Store the volume flag (alloc, unalloc, meta)

1.2.3 (2013-12-10)
------------------
* Add support for pretty mount point names

1.2.2 (2013-12-09)
------------------
* Fix issue where 'extended' is detected as ext (again)

1.2.1 (2013-12-09)
------------------
* Fix issue where 'extended' is detected as ext
* ImagePartition is now Volume

1.2.0 (2013-12-05)
------------------
* ImagePartition is now responsible for mounting and obtaining its stats, and detecting lvm volumes
* LVM partitions are now mounted using this new mount method
* Utilize the partition size for disk size, which is more reliable
* Renamed ImagePartition to Volume (no backwards compatibility is provided)
* Add unknown mount type, for use with --fstype, which mounts without knowing anything
* Support mounting a directory containing *.001/*.E01 files

1.1.2 (2013-12-05)
------------------
* Resolve bug with respect to determining free loopback device

1.1.1 (2013-12-04)
------------------
* Improve --clean by showing the commands to be executed beforehand

1.1.0 (2013-12-04)
------------------
* Do not add sudo to internal commands anymore
* --loopback is removed, detects it automatically now
* --clean is added; will remove all traces of an unsuccessful previous run

1.0.4 (2013-12-03)
------------------
* Add the any vstype
* Fix some errors in the mount_images script

1.0.3 (2013-12-02)
------------------
* Support forcing the fstype
* Improved LVM support
* Added some warnings to CLI

1.0.2 (2013-11-28)
------------------
* Improved NTFS support

1.0.1 (2013-11-28)
------------------
* command_exists now works properly

1.0.0 (2013-11-28)
------------------
* Now includes proper setup.py and versioning
* Add support for reconstructing the filesystem using bindmounts
* More reliable use of fsstat
* Overhauled Python API with more transparency and less CLI requirements
  * Store yielded information in a ImagePartition
  * Remove dependency on args and add them to the class explicitly
  * Do not depend on user interaction or CLI output in ImageParser or util, but do CLI in __main__
* Support for LVM
* Support for ewfmount
* Retrieve stats more reliably
* New CLI arguments:
  * Colored output with --color
  * Wait for warnings with --wait
  * Support for automatic method with --method=auto
  * Specify custom mount dir with --mountdir
  * Specify explicit volume system type with --vstype
  * Specify explicit file system type with --fstype
  * Specify loopback device with --loopback (required by LVM support)