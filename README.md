# insert_umat_utan_into_object_files_Fortran_LS-Dyna
A python script to enter umat and utan subroutines from a single file into multiple object files.

## The goal
We develop user-defined material models (umat) in LS-Dyna as Fortran routines. We would like to use the umats in different releases, for instance R9.2 and R11.1 and R10.2mpp. However, in LS-Dyna each release has its own object files (a folder with Fortran routines) and we would need to copy our umat into the Fortran files of each object version. To automate this process, the here provided python script automaticall copies the content from a single file into all desired LS-Dyna object version.

## NOT YET FINISHED, examples and docu will follow
