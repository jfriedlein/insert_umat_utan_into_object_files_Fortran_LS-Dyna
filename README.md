# insert_umat_utan_into_object_files_Fortran_LS-Dyna
A python script to enter umat and utan subroutines from a single file into multiple object files.

## The goal
We develop user-defined material models (umat) in LS-Dyna as Fortran routines. We would like to use the umats in different releases, for instance R9.2 and R11.1 and R10.2mpp. However, in LS-Dyna each release has its own object files (a folder with Fortran routines) and we would need to copy our umat into the Fortran files of each object version. To automate this process, the here provided python script automatically copies the content from a single file named "content_umat_utan.f" into all desired LS-Dyna object version.


## Set up the files and folders
First, download the Python script "insert_content_umat_utan.py" and the Fortran file "content_umat_utan.f".

Place both files into a folder named "insert_umat_utan_into_object_files_Fortran_LS-Dyna" (This folder should be automatically created once you download, pull or clone the repository.)

Download and extract all the LS-Dyna releases you want, for instance R11.1, R9.2, ....

Place the LS-Dyna releases and the "insert_umat_utan_into_object_files_Fortran_LS-Dyna" into one folder (this is probably not necessary, but the paths have not yet been tested for other folder structures). This folder should then look like this:

<img src="https://github.com/jfriedlein/insert_umat_utan_into_object_files_Fortran_LS-Dyna/blob/main/folder%20setup.png" width="500">

## Set up the Python script for your desired LS-Dyna releases
Open the "insert_content_umat_utan.py" file. Therein, you find a class called "LSD_release" that contains all relevant information for a specific LS-Dyna release. Look at the provided examples to see how to insert what. For instance the first entry is the path to the dyn21* files relative to the "insert_content_umat_utan.py" file. This is followed by the filenames for the umat and utans with their extension. For older releases, where everything is included in "dyn21.f", simply provide this name for both umat and utan and shown in the example for R9.2. Create such an instance for all the releases you want/need.

In the list "LSD_versions_to_be_inserted" you can insert the names that shall be worked on. Here, for instance we want to insert our code from "content_umat_utan.f" into the releases named " LSD_R920_LT7", "LSD_R111_LT7" and "LSD_R130".

```python
LSD_versions_to_be_inserted = [ LSD_R920_LT7 , LSD_R111_LT7 , LSD_R130 ]
```

The Python script can also compile the modified Fortran files by executing "make" in the directories (compile_Fortran_files=True). This requires the correct Fortran compilers and works currently only under Linux (for Windows we need to execute "nmake" in a compiler command window, see []())


## Usage: Implement your code
Instead of implementing your code directly into the 'dyn21.f' or 'dyn21umats.f'/'dyn21utan.f' files, you now need to put it into the "content_umat_utan.f" file, whose content will then be inserted into the releases.

Open the "content_umat_utan.f" Fortran file, for instance in an IDE of your choice. (Currently I cannot recommend a good IDE for Fortran, please let me know if you've found one.)

Between the `!CUSTOM_SECTION_UMAT_INCLUDE_START` and `!CUSTOM_SECTION_UMAT_INCLUDE_END` flag you can insert include files that you want/need for your umat routines, for instance

```fortran
!CUSTOM_SECTION_UMAT_INCLUDE_START
c
c hypoelasto-plasticity code
      include '../UMAT_LS-Dyna_Fortran/
     &plasti_hypo.f'
c
!CUSTOM_SECTION_UMAT_INCLUDE_END
```

Your umats can then be inserted as in the classical 'dyn21.f' or 'dyn21umats.f' files, for instance as

```fortran
      subroutine umat43(cm,eps,sig,epsp,hsv,dt1,capa,etype,tt,
     1 temper,failel,crv,nnpcrv,cma,qmat,elsiz,idele,reject)
c
c******************************************************************
c|  Livermore Software Technology Corporation  (LSTC)             |
c|  ------------------------------------------------------------  |
c|  Copyright 1987-2008 Livermore Software Tech. Corp             |
c|  All rights reserved                                           |
c******************************************************************
c hypoelasto-plasticity
c******************************************************************
c
      call plasti_hypo (cm,eps,sig,epsp,
     & hsv,dt1,capa,etype,tt,
     & temper,failel,crv,nnpcrv,cma,qmat,elsiz,idele,reject)
c
      return
      end
```

The user-defined tangents (if necessary) are followed similarly.

Between the `!CUSTOM_SECTION_UTAN_INCLUDE_START` and `!CUSTOM_SECTION_UTAN_INCLUDE_END` flag you can insert include files that you want/need for your utan routines, for instance

```fortran
!CUSTOM_SECTION_UTAN_INCLUDE_START
c
      include '../UMAT_LS-Dyna_Fortran/
     &get_utan_from_hsv.f'
c
!CUSTOM_SECTION_UTAN_INCLUDE_END
```

Your utans can then be inserted as in the classical 'dyn21.f' or 'dyn21utan.f' files, for instance as

```fortran
      subroutine utan43(cm,eps,sig,epsp,hsv,dt1,unsym,capa,etype,tt,
     1 temper,es,crv,nnpcrv,failel,cma,qmat)
c
c******************************************************************
c|  Livermore Software Technology Corporation  (LSTC)             |
c|  ------------------------------------------------------------  |
c|  Copyright 1987-2008 Livermore Software Tech. Corp             |
c|  All rights reserved                                           |
c******************************************************************
c
      call get_utan_from_hsv(cm,eps,sig,epsp,hsv,
     & dt1,unsym,capa,etype,tt,
     & temper,es,crv,nnpcrv,failel,cma,qmat)
c
      return
      end
```

## Run: Insert your code into the selected releases
Execute the Python script via the command window in its folder ("python3 insert_content_umat_utan.py"). The script will insert the Fortran code from "content_umat_utan.f" into the releases one by one, showing its action in the command window.

```shell
$ python3 insert_content_umat_utan.py 

We operate on LS-Dyna release ../ls-dyna_smp_d_r920_x64_redhat59_ifort160_MASK
Current Time = 17:09:57
The following utans will be replaced:  [43, 44]  ...
... utans replaced.
The following umats will be replaced:  [43, 44]  ...
... umats replaced.
We operate on LS-Dyna release ../ls-dyna_smp_d_R11_1_0_x64_redhat65_ifort160_sse2_MASK
Current Time = 17:09:57
The following utans will be replaced:  [43, 44]  ...
... utans replaced.
The following umats will be replaced:  [43, 44]  ...
... umats replaced.
We operate on LS-Dyna release ../ls-dyna_smp_d_R13_0_0_x64_centos610_ifort190_MASK
Current Time = 17:09:57
The following utans will be replaced:  [43, 44]  ...
... utans replaced.
The following umats will be replaced:  [43, 44]  ...
... umats replaced.

Finished execution.

```

## What happens in the background
First, we work on the utans and collect all the utan numbers that shall be replaced by searching the "content_umat_utan.f" file for the phrases utan41, utan43, ... to get the utan_nbr = [41,43,...].

We save the original dyn21-files with the name addition "_ORIGINAL" and use these versions as basis for all insertion. This means we start from the "_ORIGIINAL" file for each code insertion.

Then we loop over the utan file and insert the include paths the the utan subroutines that shall be replaced.

Second, we do the same for the umats that are either inserted into dyn21.f, where we've already changed the utans, or into the separate file "dyn21umats.f" depending on the release (chosen in instance of class LSD_release).

If desired, we compile the Fortran files and wait for the end of the compilation to show a "failed" or "finished" message.


## todo
- Currently, everything focuses on scalar umats, try this for vectorized ones (umatv)
- The code is implemented very badly (about a hundred "if"s and flags) and does nothing more than work
